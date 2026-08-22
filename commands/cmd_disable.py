import discord
from discord import app_commands
from discord.ext import commands


class DisableCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="disable", description="Tắt bot")
    async def disable(self, interaction: discord.Interaction):
        if str(interaction.user.id) not in self.bot.settings.BOT_OWNERS:
            return await interaction.response.send_message("❌ Chỉ admin chính mới dùng được.")

        guild_id = str(interaction.guild_id)
        storage = self.bot.storage
        guild_data = storage.ensure_guild(guild_id)
        guild_data["enabled"] = False

        storage.save_permissions()
        storage.log_action({"action": "disable", "guildId": guild_id, "by": str(interaction.user.id)})
        await interaction.response.send_message("⛔ Bot đã tắt ở server này.")


async def setup(bot):
    await bot.add_cog(DisableCog(bot))
