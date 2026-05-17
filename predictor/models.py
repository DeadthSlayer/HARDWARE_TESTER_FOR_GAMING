from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PredictionResult:
    compatibility_score: int
    estimated_fps: int
    lag_chance: str
    battery_drain: str
    thermal_stress: str
    recommended_settings: str
    notes: list[str]
