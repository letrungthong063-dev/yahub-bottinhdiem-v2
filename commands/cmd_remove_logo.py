import os
import shutil
import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger("yahub-bot")


class RemoveLogoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="remove_logo", description="Xóa một bộ logo đã tạo")
    @app_commands.describe(key_logo="Tên key logo cần xóa (vd: custom1)")
    async def remove_logo(self, interaction: discord.Interaction, key_logo: str):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        storage = self.bot.storage

        if not storage.is_enabled(guild_id):
            return await interaction.response.send_message("❌ Bot chưa bật.")

        if user_id not in self.bot.settings.BOT_OWNERS and not storage.is_allowed_user(guild_id, user_id):
            return await interaction.response.send_message("❌ Bạn chưa được cấp quyền.")

        logo_dir = f"logos/{key_logo}"

        if not os.path.exists(logo_dir):
            return await interaction.response.send_message(f"❌ Không tìm thấy bộ logo `{key_logo}`.")

        try:
            shutil.rmtree(logo_dir)
        except Exception as e:
            logger.error(f"[REMOVE_LOGO] Lỗi xóa bộ logo {key_logo}: {e}")
            return await interaction.response.send_message(f"❌ Lỗi khi xóa bộ logo `{key_logo}`.")

        storage.log_action({
            "action": "remove_logo", "guildId": guild_id,
            "by": user_id, "key_logo": key_logo,
        })
        await interaction.response.send_message(f"✅ Đã xóa bộ logo `{key_logo}`.")


async def setup(bot):
    await bot.add_cog(RemoveLogoCog(bot))
