import discord
from discord.ext import commands

from time import perf_counter
from random import randint

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        start = perf_counter()
        message = await ctx.send("Testing...")
        latency = (perf_counter() - start) * 1000
        await message.edit(content=f"Pong!\nLatency: {latency:.2f}ms\nAPI Latency: {self.bot.latency * 1000:.2f}ms")

    @commands.command()
    async def quote(self, ctx):
        async with self.bot.aiosession.get("https://zenquotes.io/api/random/") as response:
            if response.status == 200:
                data = await response.json()
                await ctx.send(f"\"{data[0]['q']}\" - {data[0]['a']}")

    @commands.command()
    async def xkcd(self, ctx, number: int = None):
        if number is None:
            async with self.bot.aiosession.get("https://xkcd.com/info.0.json") as response:
                if response.status == 200:
                    data = await response.json()
                    randnum = randint(1, data["num"])
                    async with self.bot.aiosession.get(f"https://xkcd.com/{randnum}/info.0.json") as response:
                        if response.status == 200:
                            data = await response.json()
                            embed = discord.Embed(
                                title=data["title"],
                                description=data["alt"],
                                url=f"https://xkcd.com/{randnum}",
                                image=data["img"],
                            )
                            embed.set_footer(text=f"{randnum} ({data['month']}/{data['day']}/{data['year']})")
                            await ctx.send(embed=embed)

        else:
            async with self.bot.aiosession.get(f"https://xkcd.com/{number}/info.0.json") as response:
                if response.status == 200:
                    data = await response.json()
                    embed = discord.Embed(
                        title=data["title"],
                        description=data["alt"],
                        url=f"https://xkcd.com/{number}",
                        image=data["img"],
                    )
                    embed.set_footer(text=f"{number} ({data['month']}/{data['day']}/{data['year']})")
                    await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(FunCommands(bot))
