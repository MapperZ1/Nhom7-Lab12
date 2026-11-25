"""
Save progress manager for Robo-Logic: Boss Battle.
Persists defeated Boss stages, 1-shot badges, and audio preference in save.json.
"""

import os
import json
from src.config import get_app_dir

SAVE_FILE = os.path.join(get_app_dir(), "save.json")


class SaveManager:
    def __init__(self, filename=SAVE_FILE):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        default_data = {
            "sound_enabled": True,
            "boss_stages": {}
        }
        if not os.path.exists(self.filename):
            return default_data

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[SaveManager] Error reading {self.filename}: {e}")
            return default_data

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[SaveManager] Error saving to {self.filename}: {e}")

    def is_boss_slain(self, stage: int) -> bool:
        boss_data = self.data.get("boss_stages", {}).get(str(stage), {})
        return boss_data.get("slain", False)

    def is_boss_one_shot(self, stage: int) -> bool:
        boss_data = self.data.get("boss_stages", {}).get(str(stage), {})
        return boss_data.get("one_shot", False)

    def record_boss_defeat(self, stage: int, is_one_shot: bool = False, attempts: int = 1):
        if "boss_stages" not in self.data:
            self.data["boss_stages"] = {}
        stage_str = str(stage)
        current = self.data["boss_stages"].get(stage_str, {})
        already_one_shot = current.get("one_shot", False) or is_one_shot
        self.data["boss_stages"][stage_str] = {
            "slain": True,
            "one_shot": already_one_shot,
            "attempts": attempts
        }
        self.save()


save_manager = SaveManager()
