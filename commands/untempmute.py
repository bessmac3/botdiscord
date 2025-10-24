# commands/untempmute.py
import discord
from discord.ext import commands
from discord import app_commands
from .utils import is_command_allowed

class UnTempMute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="untempmute", description="Retire le timeout d'un membre.")
    @app_commands.describe(member="Membre à libérer du timeout", reason="Raison (optionnel)")
    async def untempmute(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if not is_command_allowed(interaction):
            await interaction.response.send_message("Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True)
            return

        try:
            await member.edit(timed_out_until=None, reason=reason)
            await interaction.response.send_message(f"{member.mention} n'est plus en timeout.")
        except Exception as e:
            await interaction.response.send_message(f"Impossible d'enlever le timeout : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnTempMute(bot))
