# commands/utils.py
import discord

def is_command_allowed(interaction: discord.Interaction) -> bool:
    """
    Retourne True si l'utilisateur qui invoque la commande est:
     - le propriétaire du guild (guild.owner)
     - OU possède un rôle dont le nom (insensible à la casse) est 'bot'
    """
    if interaction.guild is None:
        return False

    if interaction.user == interaction.guild.owner:
        return True

    for r in getattr(interaction.user, "roles", []):
        if r and r.name.lower() == "bot":
            return True

    return False

def is_protected_member(member: discord.Member) -> bool:
    """
    Retourne True si le membre a le rôle 'Protect' (insensible à la casse).
    """
    if not isinstance(member, discord.Member):
        return False
    for r in getattr(member, "roles", []):
        if r and r.name.lower() == "protect":
            return True
    return False

# ----- setup minimal pour que le loader d'extensions ne plante pas -----
async def setup(bot):
    # module utilitaire : rien à ajouter comme cog.
    return
