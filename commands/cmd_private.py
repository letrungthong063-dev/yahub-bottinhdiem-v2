import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger("yahub-bot")


class PrivateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="private", description="Chỉ user được cấp quyền mới dùng được bot")
    async def private(self, interaction: discord.Interaction):
        if str(interaction.user.id) not in self.bot.settings.BOT_OWNERS:
            return await interaction.response.send_message("❌ Chỉ admin chính mới dùng được.")

        guild_id = str(interaction.guild_id)
        storage = self.bot.storage
        guild_data = storage.ensure_guild(guild_id)
        guild_data["public"] = False

        storage.save_permissions()
        storage.log_action({"action": "private", "guildId": guild_id, "by": str(interaction.user.id)})
        logger.info(f"[PRIVATE] Guild: {interaction.guild} by {interaction.user}")
        await interaction.response.send_message(
            "⛔ Đã tắt chế độ công khai — chỉ user được cấp quyền mới dùng được bot."
        )


async def setup(bot):
    await bot.add_cog(PrivateCog(bot))
