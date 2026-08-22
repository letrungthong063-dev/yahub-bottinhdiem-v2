"""Quản lý cooldown theo key (guild_id + user_id)."""

import asyncio
import time


class CooldownManager:
    def __init__(self):
        self._cooldowns: dict[str, float] = {}

    def remaining(self, key: str) -> int:
        """Trả về số giây còn lại của cooldown, 0 nếu không còn cooldown."""
        now = time.time()
        if key in self._cooldowns and now < self._cooldowns[key]:
            return int(self._cooldowns[key] - now)
        return 0

    def set(self, key: str, seconds: float = 10):
        self._cooldowns[key] = time.time() + seconds

    async def cleanup_loop(self, logger, interval: int = 300):
        while True:
            await asyncio.sleep(interval)
            now = time.time()
            expired = [k for k, v in self._cooldowns.items() if now > v]
            for k in expired:
                del self._cooldowns[k]
            if expired:
                logger.info(f"Đã dọn {len(expired)} cooldown hết hạn")
