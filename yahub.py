import os
import time
import discord
from discord.ext import commands

from core.logging_setup import setup_logging
from core.config import Settings
from core.storage import Storage
from core.cooldown import CooldownManager
from core.health_server import start_health_server
from core.render_service import get_available_backgrounds

logger = setup_logging()
settings = Settings()

intents = discord.Intents.default()


class YahubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.settings = settings
        self.storage = Storage()
        self.cooldowns = CooldownManager()
        self.start_time = time.time()

    async def setup_hook(self):
        commands_dir = os.path.join(os.path.dirname(__file__), "commands")
        loaded = 0
        for fname in sorted(os.listdir(commands_dir)):
            if fname.startswith("cmd_") and fname.endswith(".py"):
                ext = f"commands.{fname[:-3]}"
                try:
                    await self.load_extension(ext)
                    loaded += 1
                except Exception as e:
                    logger.error(f"❌ Lỗi nạp {ext}: {e}")
        logger.info(f"Đã nạp {loaded} lệnh từ commands/")

        synced = await self.tree.sync()
        logger.info(f"Đã sync {len(synced)} slash command lên Discord")

    async def on_ready(self):
        bgs = get_available_backgrounds()
        logger.info(f"Bot online: {self.user} | Servers: {len(self.guilds)} | Backgrounds: {bgs}")
        self.loop.create_task(self.cooldowns.cleanup_loop(logger))


def main():
    start_health_server()
    bot = YahubBot()
    bot.run(settings.TOKEN)


if __name__ == "__main__":
    main()
