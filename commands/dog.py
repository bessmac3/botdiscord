# commands/dog.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import asyncio
import discord.utils

from .utils import is_command_allowed  # utilise le helper existant

DOG_DURATION_SECONDS = 5 * 60  # 5 minutes

class Dog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # tracked : dict[(guild_id, member_id)] = {"nick": str, "until": datetime}
        self.tracked = {}

    # description raccourcie pour respecter la limite de 100 chars
    @app_commands.command(name="dog", description="Renomme quelqu'un en '🐕 de {toi}' et le surveille 5 minutes.")
    @app_commands.describe(member="Membre à renommer")
    async def dog(self, interaction: discord.Interaction, member: discord.Member):
        if not is_command_allowed(interaction):
            await interaction.response.send_message("Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True)
            return

        executor_name = interaction.user.display_name
        desired_nick = f"🐕 de {executor_name}"

        if not interaction.guild.me.guild_permissions.manage_nicknames:
            await interaction.response.send_message("Le bot n'a pas la permission `Manage Nicknames`.", ephemeral=True)
            return

        try:
            await member.edit(nick=desired_nick, reason=f"/dog utilisé par {interaction.user}")
        except Exception as e:
            await interaction.response.send_message(f"Impossible de renommer {member.mention} : {e}", ephemeral=True)
            return

        until = discord.utils.utcnow() + timedelta(seconds=DOG_DURATION_SECONDS)
        key = (interaction.guild.id, member.id)
        self.tracked[key] = {"nick": desired_nick, "until": until}

        # lancer la tâche de fin de tracking (idempotent si déjà lancée)
        asyncio.create_task(self._end_tracking_after(interaction.guild.id, member.id, DOG_DURATION_SECONDS))

        await interaction.response.send_message(f"{member.mention} renommé en **{desired_nick}** — suivi 5 minutes.", ephemeral=False)

    async def _end_tracking_after(self, guild_id: int, member_id: int, delay: int):
        await asyncio.sleep(delay)
        key = (guild_id, member_id)
        if key in self.tracked:
            del self.tracked[key]

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # si pas de changement de pseudo, on ignore
        try:
            if before.nick == after.nick:
                return
        except Exception:
            return

        key = (after.guild.id, after.id)
        entry = self.tracked.get(key)
        if not entry:
            return

        desired = entry["nick"]
        if after.nick == desired:
            return

        if entry["until"] <= discord.utils.utcnow():
            try:
                del self.tracked[key]
            except KeyError:
                pass
            return

        try:
            await after.edit(nick=desired, reason="Réappliqué par /dog (suivi actif)")
        except Exception as e:
            print(f"[dog] Impossible de remettre le pseudo pour {after} sur {after.guild}: {e}")

# setup pour le loader d'extensions
async def setup(bot):
    await bot.add_cog(Dog(bot))
