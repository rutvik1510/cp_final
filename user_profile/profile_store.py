import json
import os
from datetime import datetime

class UserProfileStore:
    """JSON file-backed user profile storage. One file per user."""

    def __init__(self, profiles_dir: str = "data/profiles"):
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)

    def _path(self, user_id: str) -> str:
        return os.path.join(self.profiles_dir, f"{user_id}.json")

    def get_profile(self, user_id: str) -> dict | None:
        path = self._path(user_id)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None

    def save_profile(self, user_id: str, profile: dict):
        profile["last_interaction"] = datetime.utcnow().isoformat()
        with open(self._path(user_id), "w") as f:
            json.dump(profile, f, indent=2)

    def get_or_create(self, user_id: str) -> dict:
        profile = self.get_profile(user_id)
        if not profile:
            profile = {
                "user_id": user_id,
                "experience_level": "unknown",
                "preferred_detail_level": "verbose",  # default to verbose
                "profiling_complete": False,
                "session_count": 0,
            }
            self.save_profile(user_id, profile)
        return profile
