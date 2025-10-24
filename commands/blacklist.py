# commands/blacklist.py
import discord
from discord.ext import commands
from discord import app_commands
from pathlib import Path
import json
from .utils import is_command_allowed, is_protected_member

DATA_FILE = Path("data/blacklist.json")

def load_blacklist():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("[]", encoding="utf-8")
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_blacklist(lst):
    DATA_FILE.write_text(json.dumps(lst, indent=2), encoding="utf-8")

class Blacklist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bl", description="Blacklist + banne un utilisateur (ban permanent tant qu'il est en blacklist).")
    @app_commands.describe(user="Utilisateur à blacklister", reason="Raison (optionnel)")
    async def bl(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        if not is_command_allowed(interaction):
            await interaction.response.send_message("Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True)
            return

        # Si l'utilisateur est présent sur le serveur, vérifier rôle Protect
        member = interaction.guild.get_member(user.id)
        if member and is_protected_member(member):
            await interaction.response.send_message(f"{member.mention} est protégé et ne peut pas être blacklisté.", ephemeral=True)
            return

        bl = load_blacklist()
        if str(user.id) in bl:
            await interaction.response.send_message(f"{user} est déjà blacklisté.", ephemeral=True)
            return

        bl.append(str(user.id))
        save_blacklist(bl)

        # bannir s'il est présent sur le serveur
        try:
            if member:
                await interaction.guild.ban(member, reason=f"Blacklist permanent: {reason or 'non spécifiée'}")
            else:
                await interaction.guild.ban(user, reason=f"Blacklist permanent: {reason or 'non spécifiée'}")
            await interaction.response.send_message(f"{user} ajouté à la blacklist et banni (si présent).")
        except Exception as e:
            await interaction.response.send_message(f"Erreur lors du ban/blacklist: {e}", ephemeral=True)

    @app_commands.command(name="unbl", description="Retirer un utilisateur de la blacklist.")
    @app_commands.describe(user="Utilisateur à retirer de la blacklist")
    async def unbl(self, interaction: discord.Interaction, user: discord.User):
        if not is_command_allowed(interaction):
            await interaction.response.send_message("Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True)
            return

        bl = load_blacklist()
        if str(user.id) not in bl:
            await interaction.response.send_message(f"{user} n'est pas dans la blacklist.", ephemeral=True)
            return

        bl.remove(str(user.id))
        save_blacklist(bl)
        await interaction.response.send_message(f"{user} retiré(e) de la blacklist.")

async def setup(bot):
    await bot.add_cog(Blacklist(bot))
