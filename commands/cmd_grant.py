import discord
from discord import app_commands
from discord.ext import commands


class GrantCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="grant", description="Cấp quyền user")
    @app_commands.describe(user="User")
    async def grant(self, interaction: discord.Interaction, user: discord.User):
        if str(interaction.user.id) not in self.bot.settings.BOT_OWNERS:
            return await interaction.response.send_message("❌ Chỉ admin chính mới dùng được, hãy liên hệ admin để được hổ trợ.")

        guild_id = str(interaction.guild_id)
        storage = self.bot.storage
        guild_data = storage.ensure_guild(guild_id)

        if str(user.id) not in guild_data["allowedUsers"]:
            guild_data["allowedUsers"].append(str(user.id))

        storage.save_permissions()
        storage.log_action({
            "action": "grant", "guildId": guild_id,
            "by": str(interaction.user.id), "target": str(user.id),
        })
        await interaction.response.send_message(f"✅ Đã cấp quyền cho {user}, hãy trai nghiệm bot và liên hệ admin nếu có vấn đề.")


async def setup(bot):
    await bot.add_cog(GrantCog(bot))
