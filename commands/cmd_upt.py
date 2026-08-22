import time
import discord
from discord import app_commands
from discord.ext import commands


class UptCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="upt", description="Trạng thái bot")
    async def upt(self, interaction: discord.Interaction):
        if str(interaction.user.id) not in self.bot.settings.BOT_OWNERS:
            return await interaction.response.send_message("❌ Chỉ admin chính mới dùng được.")

        uptime_seconds = int(time.time() - self.bot.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60

        latency = round(self.bot.latency * 1000, 1)
        server_count = len(self.bot.guilds)

        msg = "**[BOT STATUS]**\n"
        msg += f"|-- Uptime  : `{hours}h {minutes}m {seconds}s`\n"
        msg += f"|-- Speed   : `{latency}ms`\n"
        msg += f"|-- Servers : `{server_count} server`"

        await interaction.response.send_message(msg)


async def setup(bot):
    await bot.add_cog(UptCog(bot))
