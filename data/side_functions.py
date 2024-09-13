import json

from pathlib import Path
from typing import Dict, Any


class SideFunctions:
    def __init__(self) -> None:
        self.config: Dict[str, Any] = self.load_config()
        self.version: str = self.get_version()

    def load_config(self) -> Dict[str, Any]:
        config_path = Path("config.json")
        try:
            with config_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"cleanup": False}

    def save_config(self) -> None:
        config_path = Path("config.json")
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    @staticmethod
    def clean_up_cache() -> None:
        for p in Path(".").rglob("*.py[co]"):
            p.unlink()
        for p in Path(".").rglob("__pycache__"):
            p.rmdir()

    def get_version(self) -> str:
        version_file = Path(__file__).parent / "version.txt"
        try:
            with version_file.open("r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "Unknown"
