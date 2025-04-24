import re
import typing

import discord
from discord import app_commands
from discord.ext import commands


def process_relay_chat(bot, message) -> typing.Tuple[discord.Message, bool]:
    if message.channel.id == bot.config["channels"]["gamechat"]:
        match = bot.relay_regex.match(message.content)
        if match:
            author, content = match.groups()
            message.author = author
            message.content = content
            return message, True
    return message, False

async def process_custom_command(bot, message) -> bool:
    commands = bot.database.commands_cache
    for prefix in bot.command_prefix:
        if message.content.removeprefix(prefix) in commands:
            bot.logger.info(
                f"User '{message.author}' ran custom command '{message.content[1:]}'"
            )
            await message.channel.send(commands[message.content.removeprefix(prefix)])
            return True
    return False


def load_automod_regexes(bot):
    bot.automod_regexes = [re.compile(regex) for regex in bot.config["automod_regexes"]]


def find_automod_matches(bot, message: discord.Message) -> bool:
    for regex in bot.automod_regexes:
        if regex.search(message.content) is not None:
            return True
    return False


def is_staff():
    def predicate(ctx):
        if (
            discord.utils.get(ctx.author.roles, id=ctx.bot.config["roles"]["staff"])
            is not None
        ):
            return True
        else:
            raise commands.MissingPermissions("You are not staff.")

    return commands.check(predicate)

def app_is_staff():
    def predicate(interaction: discord.Interaction):
        if (
            discord.utils.get(interaction.user.roles, id=interaction.client.config["roles"]["staff"])
            is not None
        ):
            return True
        else:
            raise commands.MissingPermissions("You are not staff.")
    return app_commands.check(predicate)


def is_admin():
    def predicate(ctx):
        if (
            discord.utils.get(ctx.author.roles, id=ctx.bot.config["roles"]["admin"])
            is not None
        ):
            return True
        else:
            raise commands.MissingPermissions("You are not an admin.")

    return commands.check(predicate)

def app_is_admin():
    def predicate(interaction: discord.Interaction):
        if (
            discord.utils.get(interaction.user.roles, id=interaction.client.config["roles"]["admin"])
            is not None
        ):
            return True
        else:
            raise commands.MissingPermissions("You are not an admin.")
    return app_commands.check(predicate)
