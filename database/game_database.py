from __future__ import annotations

import json
from pathlib import Path


class GameDatabase:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.items = self._load()

    def _load(self) -> list[dict]:
        if not self.path.exists():
            raise FileNotFoundError(f"Database file not found: {self.path}")
        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data["items"]

    def search(self, query: str) -> list[dict]:
        query = query.lower()
        matches = []
        for item in self.items:
            haystack = " ".join([item["name"], item["type"], *item.get("aliases", [])]).lower()
            if query in haystack:
                matches.append(item)
        return matches

    def all(self) -> list[dict]:
        return self.items
