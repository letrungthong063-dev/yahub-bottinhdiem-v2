import discord
from discord import app_commands
from discord.ext import commands


class ListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="list", description="Xem danh sách user được cấp quyền")
    async def list_users(self, interaction: discord.Interaction):
        if str(interaction.user.id) not in self.bot.settings.BOT_OWNERS:
            return await interaction.response.send_message("❌ Chỉ admin chính mới dùng được.")

        guild_id = str(interaction.guild_id)
        storage = self.bot.storage

        if guild_id not in storage.permissions or not storage.permissions[guild_id]["allowedUsers"]:
            return await interaction.response.send_message("Không có user nào được cấp quyền.")

        text = "👥 Danh sách user được cấp quyền:\n\n"
        for uid in storage.permissions[guild_id]["allowedUsers"]:
            text += f"<@{uid}>\n"

        await interaction.response.send_message(text)


async def setup(bot):
    await bot.add_cog(ListCog(bot))
