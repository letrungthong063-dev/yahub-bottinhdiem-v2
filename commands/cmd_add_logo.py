import os
import logging
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger("yahub-bot")


class AddLogoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_logo", description="Thêm logo cho đội")
    @app_commands.describe(
        key_logo="Tên key logo (vd: custom1)",
        logo_1="Logo đội 1", id_1="ID người chơi đội 1",
        logo_2="Logo đội 2", id_2="ID người chơi đội 2",
        logo_3="Logo đội 3", id_3="ID người chơi đội 3",
        logo_4="Logo đội 4", id_4="ID người chơi đội 4",
        logo_5="Logo đội 5", id_5="ID người chơi đội 5",
        logo_6="Logo đội 6", id_6="ID người chơi đội 6",
        logo_7="Logo đội 7", id_7="ID người chơi đội 7",
        logo_8="Logo đội 8", id_8="ID người chơi đội 8",
        logo_9="Logo đội 9", id_9="ID người chơi đội 9",
        logo_10="Logo đội 10", id_10="ID người chơi đội 10",
        logo_11="Logo đội 11", id_11="ID người chơi đội 11",
        logo_12="Logo đội 12", id_12="ID người chơi đội 12",
    )
    async def add_logo(
        self,
        interaction: discord.Interaction,
        key_logo: str,
        logo_1: discord.Attachment, id_1: str,
        logo_2: discord.Attachment = None, id_2: str = "",
        logo_3: discord.Attachment = None, id_3: str = "",
        logo_4: discord.Attachment = None, id_4: str = "",
        logo_5: discord.Attachment = None, id_5: str = "",
        logo_6: discord.Attachment = None, id_6: str = "",
        logo_7: discord.Attachment = None, id_7: str = "",
        logo_8: discord.Attachment = None, id_8: str = "",
        logo_9: discord.Attachment = None, id_9: str = "",
        logo_10: discord.Attachment = None, id_10: str = "",
        logo_11: discord.Attachment = None, id_11: str = "",
        logo_12: discord.Attachment = None, id_12: str = "",
    ):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        storage = self.bot.storage

        if not storage.is_enabled(guild_id):
            return await interaction.response.send_message("❌ Bot chưa bật.")

        if user_id not in self.bot.settings.BOT_OWNERS and not storage.is_allowed_user(guild_id, user_id):
            return await interaction.response.send_message("❌ Bạn chưa được cấp quyền.")

        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            logger.warning("[ADD_LOGO] Interaction hết hạn trước khi defer.")
            return
        except Exception as e:
            logger.error(f"[ADD_LOGO] Lỗi defer: {e}")
            return

        logo_dir = f"logos/{key_logo}"
        os.makedirs(logo_dir, exist_ok=True)

        pairs = [
            (logo_1, id_1), (logo_2, id_2), (logo_3, id_3), (logo_4, id_4),
            (logo_5, id_5), (logo_6, id_6), (logo_7, id_7), (logo_8, id_8),
            (logo_9, id_9), (logo_10, id_10), (logo_11, id_11), (logo_12, id_12),
        ]

        saved = []
        errors = []

        async with aiohttp.ClientSession() as session:
            for logo_att, team_id in pairs:
                if not logo_att or not team_id.strip():
                    continue
                team_id = team_id.strip()
                if len(team_id) < 3:
                    errors.append(f"ID quá ngắn: `{team_id}`")
                    continue
                id_prefix = team_id[:-2]
                file_path = f"{logo_dir}/{id_prefix}.png"
                async with session.get(logo_att.url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        with open(file_path, "wb") as f:
                            f.write(data)
                        saved.append(f"`{team_id}`")
                    else:
                        errors.append(f"Không tải được logo của ID `{team_id}`")

        msg = f"✅ Đã lưu **{len(saved)}** logo vào bộ `{key_logo}`."
        if errors:
            msg += f"\n❌ {len(errors)} logo lỗi không lưu được."

        await interaction.followup.send(msg)


async def setup(bot):
    await bot.add_cog(AddLogoCog(bot))
