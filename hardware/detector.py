from __future__ import annotations

import platform
import shutil
import subprocess
from typing import Optional

import psutil
from rich.console import Console
from rich.prompt import Prompt

from hardware.models import HardwareProfile
from hardware.scoring import score_cpu, score_gpu, score_ram, score_storage


class HardwareDetector:
    """Detects laptop hardware and asks only for details that cannot be found."""

    def __init__(self, console: Console) -> None:
        self.console = console

    def detect(self) -> HardwareProfile:
        detected = self.detect_available()
        cpu = detected["cpu"] or self._ask("CPU not detected. Please enter CPU model")
        ram_gb = detected["ram_gb"] or self._ask_float("RAM not detected. Please enter RAM in GB")
        gpu = detected["gpu"] or self._ask("GPU not detected. Please enter GPU model")
        storage = detected["storage_type"] or self._ask_storage()
        battery = detected["battery"] or self._ask("Battery info not detected. Please enter battery status/capacity")
        os_name = detected["os"] or self._ask("Operating system not detected. Please enter OS")
        resolution = detected["screen_resolution"] or self._ask("Screen resolution not detected. Please enter resolution")

        return build_hardware_profile(cpu, ram_gb, gpu, storage, battery, os_name, resolution)

    def detect_available(self) -> dict:
        """Return hardware details without asking interactive questions."""
        return {
            "cpu": self._detect_cpu(),
            "ram_gb": self._detect_ram(),
            "gpu": self._detect_gpu(),
            "storage_type": self._detect_storage_type(),
            "battery": self._detect_battery(),
            "os": self._detect_os(),
            "screen_resolution": self._detect_screen_resolution(),
        }

    def _detect_cpu(self) -> Optional[str]:
        try:
            import cpuinfo

            brand = cpuinfo.get_cpu_info().get("brand_raw")
            if brand:
                return str(brand)
        except Exception:
            pass

        return platform.processor() or platform.machine() or None

    def _detect_ram(self) -> Optional[float]:
        try:
            return round(psutil.virtual_memory().total / (1024 ** 3), 1)
        except Exception:
            return None

    def _detect_gpu(self) -> Optional[str]:
        gpu = self._detect_gpu_with_gputil()
        if gpu:
            return gpu

        if platform.system().lower() == "windows":
            gpu = self._detect_gpu_with_wmi()
            if gpu:
                return gpu
            return self._run_powershell_gpu_query()

        return None

    def _detect_gpu_with_gputil(self) -> Optional[str]:
        try:
            import GPUtil

            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].name
        except Exception:
            return None
        return None

    def _detect_gpu_with_wmi(self) -> Optional[str]:
        try:
            import wmi

            computer = wmi.WMI()
            controllers = computer.Win32_VideoController()
            names = [controller.Name for controller in controllers if getattr(controller, "Name", None)]
            return ", ".join(names) if names else None
        except Exception:
            return None

    def _run_powershell_gpu_query(self) -> Optional[str]:
        if not shutil.which("powershell"):
            return None
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_VideoController).Name -join ', '",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            output = result.stdout.strip()
            return output or None
        except Exception:
            return None

    def _detect_storage_type(self) -> Optional[str]:
        if platform.system().lower() == "windows":
            detected = self._detect_windows_storage()
            if detected:
                return detected
        return None

    def _detect_windows_storage(self) -> Optional[str]:
        if not shutil.which("powershell"):
            return None
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-PhysicalDisk | Select-Object -First 1 -ExpandProperty MediaType)",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            storage = result.stdout.strip()
            if storage and storage.lower() != "unspecified":
                return storage
        except Exception:
            return None
        return None

    def _detect_battery(self) -> Optional[str]:
        try:
            battery = psutil.sensors_battery()
            if not battery:
                return None
            plugged = "plugged in" if battery.power_plugged else "on battery"
            return f"{battery.percent:.0f}% ({plugged})"
        except Exception:
            return None

    def _detect_os(self) -> Optional[str]:
        try:
            return f"{platform.system()} {platform.release()} ({platform.version()})"
        except Exception:
            return None

    def _detect_screen_resolution(self) -> Optional[str]:
        try:
            if platform.system().lower() == "windows":
                import ctypes

                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
                return f"{user32.GetSystemMetrics(0)}x{user32.GetSystemMetrics(1)}"
        except Exception:
            pass

        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()
            resolution = f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}"
            root.destroy()
            return resolution
        except Exception:
            return None
        return None

    def _ask(self, message: str) -> str:
        return Prompt.ask(f"[yellow]{message}[/yellow]").strip()

    def _ask_float(self, message: str) -> float:
        while True:
            value = Prompt.ask(f"[yellow]{message}[/yellow]").strip()
            try:
                return float(value)
            except ValueError:
                self.console.print("[red]Please enter a number, for example 16.[/red]")

    def _ask_storage(self) -> str:
        return Prompt.ask(
            "[yellow]Storage type not detected. Please choose storage type[/yellow]",
            choices=["NVMe SSD", "SSD", "HDD", "Hybrid"],
            default="SSD",
        )


def build_hardware_profile(
    cpu: str,
    ram_gb: float,
    gpu: str,
    storage_type: str,
    battery: str,
    os_name: str,
    screen_resolution: str,
) -> HardwareProfile:
    """Create a scored hardware profile from detected or user-entered values."""
    return HardwareProfile(
        cpu=cpu,
        ram_gb=ram_gb,
        gpu=gpu,
        storage_type=storage_type,
        battery=battery,
        os=os_name,
        screen_resolution=screen_resolution,
        cpu_score=score_cpu(cpu),
        gpu_score=score_gpu(gpu),
        ram_score=score_ram(ram_gb),
        storage_score=score_storage(storage_type),
    )
