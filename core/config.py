"""Cấu hình toàn cục: đọc .env / biến môi trường, header gọi API Garena."""

import os
import logging

logger = logging.getLogger("yahub-bot")


def _load_env(path: str = ".env") -> dict:
    env = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    env[key.strip()] = value.strip()
        logger.info("Đã load cấu hình từ file .env")
    else:
        logger.info("Không có file .env, dùng environment variables")
    return env


class Settings:
    """Gói toàn bộ cấu hình bot. Khởi tạo 1 lần trong bot.py."""

    def __init__(self):
        env = _load_env()

        def get_env(key: str, default: str = "") -> str:
            return os.environ.get(key) or env.get(key, default)

        self.TOKEN = get_env("TOKEN")
        self.CLIENT_ID = get_env("CLIENT_ID")
        self.BOT_OWNERS = [uid.strip() for uid in get_env("BOT_OWNERS").split(",") if uid.strip()]
        self.COOKIE = get_env("COOKIE")

        if not self.TOKEN:
            logger.error("Thiếu TOKEN trong file .env!")
            raise SystemExit(1)
        if not self.COOKIE:
            logger.error("Thiếu COOKIE trong file .env!")
            raise SystemExit(1)

        logger.info("Đã load cấu hình từ .env")

        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://congdong.ff.garena.vn",
            "Referer": "https://congdong.ff.garena.vn/tinh-diem",
            "Accept": "application/json, text/plain",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": self.COOKIE,
        }
