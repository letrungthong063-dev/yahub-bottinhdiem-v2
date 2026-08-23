import discord
from discord import app_commands
from discord.ext import commands


class RevokeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="revoke", description="Thu hồi quyền")
    @app_commands.describe(user="User")
    async def revoke(self, interaction: discord.Interaction, user: discord.User):
        if str(interaction.user.id) not in self.bot.settings.BOT_OWNERS:
            return await interaction.response.send_message("❌ Chỉ admin chính mới dùng được, hãy liên hệ admin để được hổ trợ.")

        guild_id = str(interaction.guild_id)
        storage = self.bot.storage

        if guild_id in storage.permissions:
            storage.permissions[guild_id]["allowedUsers"] = [
                uid for uid in storage.permissions[guild_id]["allowedUsers"]
                if uid != str(user.id)
            ]

        storage.save_permissions()
        storage.log_action({
            "action": "revoke", "guildId": guild_id,
            "by": str(interaction.user.id), "target": str(user.id),
        })
        await interaction.response.send_message(f"⛔ Đã thu hồi quyền của {user}")


async def setup(bot):
    await bot.add_cog(RevokeCog(bot))
