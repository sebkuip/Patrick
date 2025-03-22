import discord
from discord.ext import commands

async def get_custom_commands(bot) -> dict:
    return {row[0]: row[1] for row in await bot.database.get_commands()}

async def process_custom_command(bot, message) -> bool:
    commands = await get_custom_commands(bot)
    if message.content[1:] in commands:
        await message.channel.send(commands[message.content[1:]])
        return True
    return False
