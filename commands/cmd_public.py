import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger("yahub-bot")


class PublicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="public", description="Cho phép tất cả mọi người trong server dùng bot")
    async def public(self, interaction: discord.Interaction):
        if str(interaction.user.id) not in self.bot.settings.BOT_OWNERS:
            return await interaction.response.send_message("❌ Chỉ admin chính mới dùng được, hãy liên hệ admin để được hổ trợ.")

        guild_id = str(interaction.guild_id)
        storage = self.bot.storage
        guild_data = storage.ensure_guild(guild_id)
        guild_data["public"] = True

        storage.save_permissions()
        storage.log_action({"action": "public", "guildId": guild_id, "by": str(interaction.user.id)})
        logger.info(f"[PUBLIC] Guild: {interaction.guild} by {interaction.user}")
        await interaction.response.send_message(
            "✅ Đã bật chế độ **công khai** — tất cả mọi người trong server đều dùng được bot."
        )


async def setup(bot):
    await bot.add_cog(PublicCog(bot))
