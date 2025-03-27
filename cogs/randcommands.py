import asyncio
from random import choice, getrandbits, randint
from time import perf_counter

import discord
from discord.ext import commands

from util import is_staff, is_admin


class RandCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Performs a ping test and shows results.")
    async def ping(self, ctx):
        start = perf_counter()
        message = await ctx.send("Testing...")
        latency = (perf_counter() - start) * 1000
        await message.edit(
            content=f"Pong!\nLatency: {latency:.2f}ms\nAPI Latency: {self.bot.latency * 1000:.2f}ms"
        )

    @commands.command(help="Gets a random quote from zenquotes.")
    async def quote(self, ctx):
        async with self.bot.aiosession.get(
            "https://zenquotes.io/api/random/"
        ) as response:
            if response.status == 200:
                data = await response.json()
                await ctx.send(f"\"{data[0]['q']}\" - {data[0]['a']}")

    async def get_xkcd_data(self, number: int):
        async with self.bot.aiosession.get(
            f"https://xkcd.com/{number}/info.0.json"
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None

    def xkcd_embed(self, data):
        embed = discord.Embed(
            title=data["title"],
            description=data["alt"],
            url=f"https://xkcd.com/{data['num']}",
            image=data["img"],
        )
        embed.set_footer(
            text=f"{data['num']} ({data['month']}/{data['day']}/{data['year']})"
        )
        return embed

    @commands.command(help="Gets a random or specific xkcd comic.")
    async def xkcd(self, ctx, number: int = None):
        if number is None:
            async with self.bot.aiosession.get(
                "https://xkcd.com/info.0.json"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    randnum = randint(1, data["num"])
                    data = await self.get_xkcd_data(randnum)
                    if data is None:
                        return await ctx.send(
                            "An error occurred while fetching the comic."
                        )
                    await ctx.send(embed=self.xkcd_embed(data))

        else:
            data = await self.get_xkcd_data(number)
            if data is None:
                return await ctx.send("An error occurred while fetching the comic.")
            await ctx.send(embed=self.xkcd_embed(data))

    @commands.command(help="Gets a random protip.")
    async def protip(self, ctx):
        random_tip = choice(self.bot.config.get("protips"))
        await ctx.send(f"{ctx.author.display_name}: Pro Tip: {random_tip}")

    @commands.command(
        help="Generates a random binary number with the given amount of bits."
    )
    async def rng(self, ctx, num: int):
        if num < 1:
            return await ctx.send("Number must be greater than 0.")
        generated = getrandbits(num)
        await ctx.send(f"{ctx.author.display_name}: {generated:0{num}b}")

    @commands.command(help="Insult someone >:D")
    async def insult(self, ctx, member: discord.Member):
        insult = choice(self.bot.config["insults"])
        await ctx.send(insult.format(user=member.mention))

    @commands.command(help="Get someone's minecraft UUID.")
    async def uuid(self, ctx, username: str):
        async with self.bot.aiosession.get(
            f"https://api.mojang.com/users/profiles/minecraft/{username}"
        ) as response:
            if response.status == 200:
                data = await response.json()
                raw_uuid = data["id"]
                uuid = str(
                    raw_uuid[:8]
                    + "-"
                    + raw_uuid[8:12]
                    + "-"
                    + raw_uuid[12:16]
                    + "-"
                    + raw_uuid[16:20]
                    + "-"
                    + raw_uuid[20:])
                await ctx.send(f"{ctx.author.display_name}: `{uuid}`")
            else:
                await ctx.send("Invalid username provided")

    @commands.command(help="pikl someone.")
    @commands.guild_only()
    @is_staff()
    async def pikl(self, ctx, user: discord.Member):
        pikl_role = discord.utils.get(ctx.guild.roles, name="pikl")
        if pikl_role is None:
            return await ctx.send("No pikl rank :(")
        await user.add_roles(pikl_role)
        await ctx.send(f"{user.mention} got pikl'd.")
        await asyncio.sleep(120_000)
        await user.remove_roles(pikl_role)

    @commands.command(help="Run a query on the database.")
    @is_admin()
    async def query(self, ctx, *, query):
        response = await self.bot.database.query(query)
        await ctx.send(f"Succesfully ran query: {response}")

    @commands.command(help="Googles something.")
    async def google(self, ctx, *, query):
        await ctx.send(f"https://www.google.com/search?q={query.replace(' ', '+')}")

def setup(bot):
    bot.add_cog(RandCommands(bot))
