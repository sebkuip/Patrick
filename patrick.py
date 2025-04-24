import logging
import re
from os import getenv, listdir
from pathlib import Path

import discord
import yaml
from aiohttp import ClientSession
from discord.ext import commands
from dotenv import load_dotenv

import database
from util import (
    find_automod_matches,
    is_admin,
    load_automod_regexes,
    process_custom_command,
    process_relay_chat,
)

load_dotenv(Path(__file__).parent / ".env")
TOKEN: str = getenv("TOKEN")


def load_config():
    with open(Path(__file__).parent / "config.yaml", "r") as source:
        return yaml.safe_load(source)


class PatrickHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def get_commands_mapping(self) -> tuple:
        commands = {
            command.name: (
                command.signature,
                command.help if command.help is not None else "",
            )
            for command in self.context.bot.commands
        }
        custom_commands = context.bot.database.commands_cache
        return (commands, custom_commands)

    def format_table(
        self, commands_mapping: dict, custom_commands_mapping: dict
    ) -> str:
        for key, value in custom_commands_mapping.items():
            new_value = value.replace("\n", " ").replace("\r", " ").replace("\t", " ")
            custom_commands_mapping[key] = (
                new_value if len(value) < 100 else f"{new_value[:97]}..."
            )

        maxlen_key = max(
            [len(key) for key in commands_mapping.keys()] + [len("Command:")]
        )
        maxlen_value = max(
            [len(value[0]) for value in commands_mapping.values()] + [len("Message:")]
        )
        maxlen_description = max(len(value[1]) for value in commands_mapping.values())

        text = "Available commands:\n"
        text += f"|-{''.ljust(maxlen_key, '-')}-|-{''.ljust(maxlen_value, '-')}-|-{''.ljust(maxlen_description, '-')}-|\n"
        text += f"| {'Command:'.ljust(maxlen_key)} | {'Signature:'.ljust(maxlen_value)} | {'Description:'.ljust(maxlen_description)} |\n"
        text += f"|-{''.ljust(maxlen_key, '-')}-|-{''.ljust(maxlen_value, '-')}-|-{''.ljust(maxlen_description, '-')}-|\n"
        text += "\n".join(
            f"| {key.ljust(maxlen_key)} | {value[0].ljust(maxlen_value)} | {value[1].ljust(maxlen_description)} |"
            for key, value in commands_mapping.items()
        )
        text += f"\n|-{''.ljust(maxlen_key, '-')}-|-{''.ljust(maxlen_value, '-')}-|-{''.ljust(maxlen_description, '-')}-|"

        maxlen_key = max(
            [len(key) for key in custom_commands_mapping.keys()] + [len("Command:")]
        )
        maxlen_value = max(
            [len(value) for value in custom_commands_mapping.values()]
            + [len("Message:")]
        )

        text += "\n\nCustom commands:\n"
        text += f"|-{''.ljust(maxlen_key, '-')}-|-{''.ljust(maxlen_value, '-')}-|\n"
        text += (
            f"| {'Command:'.ljust(maxlen_key)} | {'Message:'.ljust(maxlen_value)} |\n"
        )
        text += f"|-{''.ljust(maxlen_key, '-')}-|-{''.ljust(maxlen_value, '-')}-|\n"
        text += "\n".join(
            f"| {key.ljust(maxlen_key)} | {value.ljust(maxlen_value)} |"
            for key, value in custom_commands_mapping.items()
        )
        text += f"\n|-{''.ljust(maxlen_key, '-')}-|-{''.ljust(maxlen_value, '-')}-|"
        return text

    async def generate_link(self, content: str) -> str:
        data = {"content": content, "title": "ORE Patrick", "expiry_days": 1}
        async with self.context.bot.aiosession.post(
            "https://dpaste.com/api/v2/", data=data
        ) as response:
            return response.headers["Location"]

    async def send_help_message(self, user: discord.User):
        commands, custom_commands = await self.get_commands_mapping()
        command_names = list(commands.keys())
        command_names += list(custom_commands.keys())
        if len(command_names) <= 7:
            return await user.send(f"Available commands: {', '.join(command_names)}")
        content = self.format_table(commands, custom_commands)
        link = await self.generate_link(content)
        return await user.send(
            f"Available commands: {', '.join(list(command_names)[:7])} ...\nSnipped: <{link}>"
        )

    async def send_bot_help(self, mapping):
        user = self.context.author
        await self.send_help_message(user)

    async def send_command_help(self, command):
        user = self.context.author
        if len(command.signature) == 0:
            await user.send(
                f"Usage: `{self.context.bot.command_prefix[1]}{command.name}`"
            )
        else:
            await user.send(
                f"Usage: `{self.context.bot.command_prefix[1]}{command.name} {command.signature}`"
            )


class Patrick(commands.Bot):
    def __init__(self, logger: logging.Logger, config: dict):
        self.logger = logger
        self.config = config
        self.database = database.Connector()
        self.relay_regex = re.compile(
            self.config.get(
                "ingame_regex", r"^`[A-Za-z]+` \*\*([A-Za-z0-9_\\]+)\*\*: *(.*)$"
            )
        )
        activity = discord.Game("with Python")

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=(", ", ","),
            case_insensitive=True,
            intents=intents,
            activity=activity,
            help_command=PatrickHelp(),
        )

    async def on_ready(self):
        self.logger.info("Connecting to database")
        await self.database.connect()
        self.aiosession = ClientSession()
        await self.load_extensions()
        self.logger.info(f"Logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        found = False
        if message.author.bot:
            if find_automod_matches(self, message):
                logger.info(
                    f"Automod triggered for user {message.author} ({message.author.id}) with message {message.content}"
                )
                await message.delete()
                return
            message, found = process_relay_chat(self, message)
        if message.content.startswith(self.command_prefix):
            if await process_custom_command(self, message):
                await self.database.add_command_history(
                    message.author.display_name, message.content
                )
                return
        if not found:
            await self.process_commands(message)

    async def process_commands(self, message: discord.Message) -> None:
        ctx = await self.get_context(message)
        if ctx.command is not None:
            self.logger.info(
                f"User '{message.author}' ran command '{ctx.command.name}'"
            )
            await self.database.add_command_history(
                message.author.display_name, ctx.command.name
            )
        await self.invoke(ctx)

    async def load_extensions(self):
        self.logger.info("Loading extensions")
        status = {}
        for extension in listdir("./cogs"):
            if extension.endswith(".py"):
                status[extension] = "X"
        if len(status) == 0:
            logger.info("No extensions found")
            return
        errors = []

        for extension in status:
            try:
                await self.load_extension(f"cogs.{extension[:-3]}")
                status[extension] = "L"
            except Exception as e:
                errors.append(e)

        maxlen = max(len(str(extension)) for extension in status)
        for extension in status:
            self.logger.info(f" {extension.ljust(maxlen)} | {status[extension]}")
        (
            self.logger.error(errors)
            if errors
            else self.logger.info("no errors during loading of extensions")
        )

    async def reload_extensions(self):
        for extension in list(self.extensions):
            self.logger.info(f"Reloading extension {extension}")
            await self.unload_extension(extension)
        await self.load_extensions()


config = load_config()
logging_level = config.get("logging_level", "").upper()
if logging_level in ("DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"):
    logging.basicConfig(level=logging.getLevelName(logging_level))
else:
    print("Invalid logging level in config.yaml, defaulting to INFO")
    logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger("patrick")
logging.basicConfig(level=logging.INFO)
patrick: Patrick = Patrick(logger, config)
load_automod_regexes(patrick)


@patrick.command(help="Reloads all extensions and configs. Admin only.")
@is_admin()
async def reload(ctx):
    await ctx.message.delete(delay=5)
    m: discord.Message = await ctx.send("Reloading extensions...")
    await patrick.reload_extensions()
    await m.edit(content="Reloaded extensions")
    await m.delete(delay=5)
    m: discord.Message = await ctx.send("Reloading config...")
    config = load_config()
    patrick.config = config
    load_automod_regexes(patrick)
    await m.edit(content="Reloaded config")
    await m.delete(delay=5)


patrick.run(TOKEN)
