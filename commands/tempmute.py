# commands/tempmute.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from .utils import is_command_allowed, is_protected_member

class TempMute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tempmute", description="Met en timeout un membre pendant X minutes.")
    @app_commands.describe(member="Membre à timeout", minutes="Durée du timeout en minutes", reason="Raison (optionnel)")
    async def tempmute(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = None):
        # check droit d'accès à la commande
        if not is_command_allowed(interaction):
            await interaction.response.send_message("Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True)
            return

        # check rôle Protect sur la cible
        if is_protected_member(member):
            await interaction.response.send_message(f"{member.mention} est protégé et ne peut pas être mis en timeout.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message("Le bot n'a pas la permission 'MODERATE_MEMBERS'.", ephemeral=True)
            return

        if minutes <= 0:
            await interaction.response.send_message("La durée doit être supérieure à 0.", ephemeral=True)
            return

        until = discord.utils.utcnow() + timedelta(minutes=minutes)
        try:
            await member.edit(timed_out_until=until, reason=reason)
            await interaction.response.send_message(f"{member.mention} a été mis en timeout pendant {minutes} minute(s).")
        except Exception as e:
            await interaction.response.send_message(f"Impossible de mettre en timeout {member.mention} : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TempMute(bot))
