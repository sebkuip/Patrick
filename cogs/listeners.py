import discord
from discord.ext import commands
from random import choice

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        greeting: str = choice(self.bot.config["greetings"])
        channel: discord.abc.Messageable = member.guild.get_channel(self.bot.config["channels"]["welcome"])
        await channel.send(greeting.format(user=member.mention))

async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))