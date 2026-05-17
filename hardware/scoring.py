from __future__ import annotations

import re


def score_cpu(cpu_name: str) -> int:
    name = cpu_name.lower()
    score = 35

    high_markers = ["i9", "ryzen 9", "ultra 9", "m3 max", "m2 max"]
    strong_markers = ["i7", "ryzen 7", "ultra 7", "m3 pro", "m2 pro", "m1 pro"]
    mid_markers = ["i5", "ryzen 5", "ultra 5", "m3", "m2", "m1"]
    entry_markers = ["i3", "ryzen 3", "pentium", "celeron", "athlon"]

    if any(marker in name for marker in high_markers):
        score = 92
    elif any(marker in name for marker in strong_markers):
        score = 78
    elif any(marker in name for marker in mid_markers):
        score = 62
    elif any(marker in name for marker in entry_markers):
        score = 42

    generation = _extract_intel_generation(name)
    if generation >= 12:
        score += 8
    elif 8 <= generation <= 11:
        score += 3
    elif 1 <= generation <= 6:
        score -= 8

    return _clamp(score)


def score_gpu(gpu_name: str) -> int:
    name = gpu_name.lower()
    score = 25

    tiers = [
        (["rtx 4090", "rtx 4080", "rx 7900"], 98),
        (["rtx 4070", "rtx 3080", "rtx 3070", "rx 7800", "rx 7700"], 88),
        (["rtx 4060", "rtx 3060", "rtx 2080", "rtx 2070", "rx 6700", "rx 6600"], 76),
        (["rtx 3050", "gtx 1660", "gtx 1650", "rx 580", "rx 570"], 58),
        (["gtx 1050", "mx450", "mx350", "vega", "iris xe", "radeon graphics"], 42),
        (["intel uhd", "intel hd", "integrated", "basic display"], 24),
    ]

    for markers, tier_score in tiers:
        if any(marker in name for marker in markers):
            score = tier_score
            break

    if "laptop" in name or "mobile" in name:
        score -= 4

    return _clamp(score)


def score_ram(ram_gb: float) -> int:
    if ram_gb >= 32:
        return 95
    if ram_gb >= 16:
        return 78
    if ram_gb >= 12:
        return 62
    if ram_gb >= 8:
        return 48
    return 28


def score_storage(storage_type: str) -> int:
    storage = storage_type.lower()
    if "nvme" in storage:
        return 95
    if "ssd" in storage:
        return 82
    if "hybrid" in storage or "sshd" in storage:
        return 55
    if "hdd" in storage:
        return 35
    return 50


def _extract_intel_generation(name: str) -> int:
    match = re.search(r"i[3579][-\s]?(\d{4,5})", name)
    if not match:
        return 0
    digits = match.group(1)
    return int(digits[:2]) if len(digits) == 5 else int(digits[0])


def _clamp(value: int) -> int:
    return max(1, min(100, value))
