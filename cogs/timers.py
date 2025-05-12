import discord
from discord.ext import commands

from database import start_timer, stop_timer, list_timers
from util import is_discord_member

class Timers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Group(name="timer", invoke_without_command=True)
    @is_discord_member()
    async def timer(self, ctx):
        """Timer commands"""
        raise commands.CommandNotFound(
            "Invalid subcommand. Use `,timer start`, `,timer stop`, or `,timer list`."
        )
    
    @timer.command(name="start")
    @is_discord_member()
    async def start_timer(self, ctx, *, name: str):
        await start_timer(ctx.author.id, name)
        await ctx.send(f"{ctx.author.display_name}: Timer '{name}' started.")

    @timer.command(name="stop")
    @is_discord_member()
    async def stop_timer(self, ctx, *, name: str):
        rows = await stop_timer(ctx.author.id, name)
        if rows:
            await ctx.send(f"{ctx.author.display_name}: Timer '{name}' stopped.")
        else:
            await ctx.send(f"{ctx.author.display_name}: No timer found with the name '{name}'.")


async def setup(bot):
    await bot.add_cog(Timers(bot))