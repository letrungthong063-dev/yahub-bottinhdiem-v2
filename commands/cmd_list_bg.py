import os
import logging
import discord
from discord import app_commands
from discord.ext import commands

from core.render_service import get_available_backgrounds

logger = logging.getLogger("yahub-bot")


class ListBgCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="list_bg", description="Xem danh sách background có sẵn")
    async def list_bg(self, interaction: discord.Interaction):
        available = get_available_backgrounds()

        if not available:
            return await interaction.response.send_message("❌ Chưa có background nào để xem.")

        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            logger.warning("[LIST_BG] Interaction hết hạn trước khi defer.")
            return
        except Exception as e:
            logger.error(f"[LIST_BG] Lỗi defer: {e}")
            return

        name_list = "\n".join(f"• `{bg}`" for bg in available)
        msg = f"🖼️ **Danh sách background có sẵn ({len(available)}):**\n{name_list}\n\n💡 Dùng: `/bxh background: <tên background>`"
        await interaction.followup.send(msg, ephemeral=True)

        for bg in available:
            bg_path = f"backgrounds/{bg}.png"
            if os.path.exists(bg_path):
                await interaction.followup.send(
                    content=f"`{bg}`",
                    file=discord.File(bg_path, filename=f"{bg}.png"),
                    ephemeral=True,
                )


async def setup(bot):
    await bot.add_cog(ListBgCog(bot))
