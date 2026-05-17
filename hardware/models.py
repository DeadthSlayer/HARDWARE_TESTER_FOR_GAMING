from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HardwareProfile:
    cpu: str
    ram_gb: float
    gpu: str
    storage_type: str
    battery: str
    os: str
    screen_resolution: str

    cpu_score: int = 0
    gpu_score: int = 0
    ram_score: int = 0
    storage_score: int = 0

    def as_dict(self) -> dict:
        return {
            "CPU": self.cpu,
            "RAM": f"{self.ram_gb:.1f} GB",
            "GPU": self.gpu,
            "Storage": self.storage_type,
            "Battery": self.battery,
            "Operating System": self.os,
            "Screen Resolution": self.screen_resolution,
        }
