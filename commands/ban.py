# commands/ban.py
import discord
from discord.ext import commands
from discord import app_commands
from .utils import is_command_allowed, is_protected_member

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Bannir un membre.")
    @app_commands.describe(member="Membre à bannir", reason="Raison (optionnel)", delete_days="Supprimer X jours de messages (0-7)")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None, delete_days: int = 0):
        # check droit d'accès
        if not is_command_allowed(interaction):
            await interaction.response.send_message("Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True)
            return

        # protect role check
        if is_protected_member(member):
            await interaction.response.send_message(f"{member.mention} est protégé et ne peut pas être banni.", ephemeral=True)
            return

        if not 0 <= delete_days <= 7:
            await interaction.response.send_message("delete_days doit être entre 0 et 7.", ephemeral=True)
            return

        try:
            await interaction.guild.ban(member, reason=reason, delete_message_days=delete_days)
            await interaction.response.send_message(f"{member.mention} a été banni. Raison: {reason or 'non spécifiée'}")
        except Exception as e:
            await interaction.response.send_message(f"Impossible de bannir: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ban(bot))
