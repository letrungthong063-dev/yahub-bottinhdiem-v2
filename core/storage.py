import json
import os
from datetime import datetime, timezone


class Storage:
    def __init__(self, permissions_path: str = "permissions.json", logs_path: str = "logs.json"):
        self.permissions_path = permissions_path
        self.logs_path = logs_path

        if not os.path.exists(self.permissions_path):
            with open(self.permissions_path, "w") as f:
                json.dump({}, f)

        if not os.path.exists(self.logs_path):
            with open(self.logs_path, "w") as f:
                json.dump([], f)

        with open(self.permissions_path, "r") as f:
            self.permissions: dict = json.load(f)

        with open(self.logs_path, "r") as f:
            self.logs: list = json.load(f)

    def save_permissions(self):
        with open(self.permissions_path, "w") as f:
            json.dump(self.permissions, f, indent=2)

    def save_logs(self):
        with open(self.logs_path, "w") as f:
            json.dump(self.logs, f, indent=2)

    def log_action(self, data: dict):
        data["time"] = datetime.now(timezone.utc).isoformat()
        self.logs.append(data)
        self.save_logs()

    def ensure_guild(self, guild_id: str):
        if guild_id not in self.permissions:
            self.permissions[guild_id] = {"enabled": False, "allowedUsers": [], "public": False}
        return self.permissions[guild_id]

    def is_enabled(self, guild_id: str) -> bool:
        return guild_id in self.permissions and self.permissions[guild_id].get("enabled", False)

    def is_public(self, guild_id: str) -> bool:
        return guild_id in self.permissions and self.permissions[guild_id].get("public", False)

    def is_allowed_user(self, guild_id: str, user_id: str) -> bool:
        if guild_id not in self.permissions:
            return False
        return user_id in self.permissions[guild_id].get("allowedUsers", [])
