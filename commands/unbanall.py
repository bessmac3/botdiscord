# commands/unbanall.py
import discord
from discord.ext import commands
from discord import app_commands
from .utils import is_command_allowed

class UnbanAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unbanall", description="Débannir tous les membres bannis du serveur.")
    async def unbanall(self, interaction: discord.Interaction):
        if not is_command_allowed(interaction):
            await interaction.response.send_message("Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True)
            return

        try:
            try:
                bans = await interaction.guild.bans()
            except TypeError:
                bans = [ban async for ban in interaction.guild.bans()]
        except Exception as e:
            await interaction.response.send_message(f"Impossible de récupérer la liste des bans: {e}", ephemeral=True)
            return

        if not bans:
            await interaction.response.send_message("Aucun membre n'est banni.")
            return

        count = 0
        errors = []
        for ban_entry in bans:
            try:
                await interaction.guild.unban(ban_entry.user, reason=f"Unban all demandé par {interaction.user}")
                count += 1
            except Exception as e:
                errors.append(f"{ban_entry.user} : {e}")
                print("Unban error:", e)

        reply = f"{count} membre(s) débannis."
        if errors:
            reply += f"\nCertaines erreurs sont survenues pour {len(errors)} entrée(s). Voir les logs."
        await interaction.response.send_message(reply)

async def setup(bot):
    await bot.add_cog(UnbanAll(bot))
