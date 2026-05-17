from __future__ import annotations

from hardware.models import HardwareProfile
from predictor.models import PredictionResult


class BasePredictionEngine:
    """Interface kept small so ML models can be added later."""

    def predict(self, hardware: HardwareProfile, target: dict) -> PredictionResult:
        raise NotImplementedError


class RuleBasedPredictionEngine(BasePredictionEngine):
    """First version of RunWise AI: transparent weighted scoring rules."""

    def predict(self, hardware: HardwareProfile, target: dict) -> PredictionResult:
        required = target["requirements"]
        minimum = required["minimum"]
        recommended = required["recommended"]

        gpu_fit = self._fit_score(hardware.gpu_score, minimum["gpu_score"], recommended["gpu_score"])
        cpu_fit = self._fit_score(hardware.cpu_score, minimum["cpu_score"], recommended["cpu_score"])
        ram_fit = self._fit_score(hardware.ram_score, minimum["ram_score"], recommended["ram_score"])
        storage_fit = self._fit_score(
            hardware.storage_score,
            minimum.get("storage_score", 35),
            recommended.get("storage_score", 70),
        )

        weighted_score = (
            gpu_fit * 0.42
            + cpu_fit * 0.28
            + ram_fit * 0.22
            + storage_fit * 0.08
        )
        compatibility = max(1, min(100, round(weighted_score)))

        fps = self._estimate_fps(compatibility, target["performance_class"])
        lag = self._lag_category(compatibility)
        battery = self._battery_category(hardware, target, compatibility)
        thermals = self._thermal_category(hardware, target, compatibility)
        settings = self._settings(compatibility)
        notes = self._build_notes(hardware, minimum, recommended, compatibility)

        return PredictionResult(
            compatibility_score=compatibility,
            estimated_fps=fps,
            lag_chance=lag,
            battery_drain=battery,
            thermal_stress=thermals,
            recommended_settings=settings,
            notes=notes,
        )

    def _fit_score(self, actual: int, minimum: int, recommended: int) -> float:
        if actual < minimum:
            return max(5, (actual / max(minimum, 1)) * 45)
        if actual >= recommended:
            extra = min(15, (actual - recommended) * 0.25)
            return min(100, 85 + extra)
        span = max(recommended - minimum, 1)
        return 50 + ((actual - minimum) / span) * 35

    def _estimate_fps(self, compatibility: int, performance_class: str) -> int:
        baselines = {
            "light": (70, 220),
            "medium": (45, 165),
            "heavy": (25, 115),
            "creative": (24, 90),
        }
        low, high = baselines.get(performance_class, (35, 140))
        fps = low + ((high - low) * compatibility / 100)
        return max(15, round(fps))

    def _lag_category(self, score: int) -> str:
        if score >= 75:
            return "Low"
        if score >= 50:
            return "Medium"
        return "High"

    def _battery_category(self, hardware: HardwareProfile, target: dict, score: int) -> str:
        load = target.get("power_load", 50)
        if "plugged" in hardware.battery.lower():
            load -= 10
        if score < 55:
            load += 15
        if load >= 75:
            return "Heavy"
        if load >= 45:
            return "Moderate"
        return "Mild"

    def _thermal_category(self, hardware: HardwareProfile, target: dict, score: int) -> str:
        heat = target.get("thermal_load", 50)
        if hardware.gpu_score < target["requirements"]["recommended"]["gpu_score"]:
            heat += 10
        if hardware.cpu_score < target["requirements"]["recommended"]["cpu_score"]:
            heat += 8
        if score >= 80:
            heat -= 10

        if heat >= 76:
            return "Hot"
        if heat >= 46:
            return "Warm"
        return "Cool"

    def _settings(self, score: int) -> str:
        if score >= 88:
            return "Ultra/High at native resolution"
        if score >= 72:
            return "High with shadows and ray tracing reduced"
        if score >= 55:
            return "Medium, use upscaling if available"
        if score >= 38:
            return "Low, 720p or performance mode recommended"
        return "Very Low; close background apps and expect compromises"

    def _build_notes(self, hardware: HardwareProfile, minimum: dict, recommended: dict, score: int) -> list[str]:
        notes: list[str] = []
        if hardware.gpu_score < minimum["gpu_score"]:
            notes.append("GPU is below the minimum target and will be the main bottleneck.")
        elif hardware.gpu_score < recommended["gpu_score"]:
            notes.append("GPU meets minimum expectations but is below the recommended tier.")

        if hardware.cpu_score < minimum["cpu_score"]:
            notes.append("CPU is below the minimum target; stutter is likely in busy scenes.")
        elif hardware.cpu_score < recommended["cpu_score"]:
            notes.append("CPU is usable, but background apps may reduce smoothness.")

        if hardware.ram_score < minimum["ram_score"]:
            notes.append("RAM is below minimum; upgrade RAM for a better experience.")
        elif hardware.ram_score < recommended["ram_score"]:
            notes.append("RAM is acceptable, but multitasking should be limited.")

        if score >= 80:
            notes.append("Overall fit looks strong for a laptop-class system.")

        return notes or ["No major bottleneck detected for the selected title."]
