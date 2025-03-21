import discord
from discord.ext import commands

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def addcommand(self, ctx, key: str, *, message: str):
        await self.bot.database.add_command(key, message)
        await ctx.send(f"Command `{key}` added.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def delcommand(self, ctx, key: str):
        await self.bot.database.remove_command(key)
        await ctx.send(f"Command `{key}` removed.")

def setup(bot):
    bot.add_cog(CustomCommands(bot))