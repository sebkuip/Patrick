import discord
from discord.ext import commands
from random import choice

from util import is_staff

class COREmands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="Shows instructions how to apply for student, builder, or engineer."
    )
    async def apply(self, ctx, *, name: str = None):
        if name is None:
            return await ctx.send('Specify "student", "builder", or "engineer".')
        match name:
            case "student":
                await ctx.send(
                    "To apply for student, hop onto `mc.openredstone.org` and run `/apply`"
                )
            case "builder":
                await ctx.send(
                    "To apply for builder, follow the steps outlined here: <https://discourse.openredstone.org/builder>"
                )
            case "engineer":
                await ctx.send(
                    "To apply for engineer, follow the steps outlined here: <https://discourse.openredstone.org/engineer>"
                )
            case _:
                await ctx.send('Specify "student", "builder", or "engineer".')

    @is_staff()
    @commands.command(help="Give the trusted role to someone.")
    async def trust(self, ctx, member: discord.Member):
        await member.add_roles(ctx.guild.get_role(self.bot.config["roles"]["trusted"]))
        await ctx.send(f"{ctx.author.display_name}: {member.display_name} is now Trusted.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        greeting = choice(self.bot.config["greetings"])
        channel = member.guild.get_channel(self.bot.config["channels"]["welcome"])
        await channel.send(greeting.format(user=member.mention))

def setup(bot):
    bot.add_cog(COREmands(bot))
