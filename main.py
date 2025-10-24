# main.py (corrigé)
import asyncio
import discord
from discord.ext import commands
import os
import json
from pathlib import Path

intents = discord.Intents.default()
intents.members = True  # nécessaire pour on_member_join
intents.guilds = True
# si tu n'utilises pas le contenu des messages, laisse message_content = False
intents.message_content = False

BOT_TOKEN = "A"  # ou récupérer depuis une variable d'environnement

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user} (id: {bot.user.id})")
    try:
        await bot.tree.sync()
        print("Slash commands sync completed.")
    except Exception as e:
        print("Erreur lors du sync des slash commands:", e)

@bot.event
async def on_member_join(member: discord.Member):
    data_file = Path("data/blacklist.json")
    if not data_file.exists():
        return
    try:
        with data_file.open("r", encoding="utf-8") as f:
            blacklist = json.load(f)
    except Exception:
        blacklist = []

    if str(member.id) in blacklist:
        # si membre a rôle Protect, ne pas re-ban
        if any(r.name.lower() == "protect" for r in member.roles):
            print(f"{member} est blacklisté mais possède le rôle Protect -> skip re-ban.")
            return

        reason = "Membre blacklisté — ban automatique à la ré-entrée."
        try:
            await member.guild.ban(member, reason=reason)
            print(f"Re-ban automatique de {member} ({member.id}) sur {member.guild.name}")
        except Exception as e:
            print(f"Impossible de re-ban {member}: {e}")


async def main():
    # charger toutes les extensions (await car load_extension est une coroutine)
    for filename in os.listdir("commands"):
        if filename.endswith(".py"):
            ext = f"commands.{filename[:-3]}"
            try:
                await bot.load_extension(ext)
                print(f"Loaded extension: {ext}")
            except Exception as e:
                print(f"Failed to load extension {ext}: {e}")

    # démarrer le bot proprement
    try:
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
