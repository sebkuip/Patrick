import re
from os import getenv, listdir
from pathlib import Path
import logging
import yaml
from dotenv import load_dotenv
from aiohttp import ClientSession

import discord
from discord.ext import commands

import database
import util

load_dotenv(Path(__file__).parent / '.env')
TOKEN: str = getenv('TOKEN')

def load_config():
    with open(Path(__file__).parent / 'config.yaml', 'r') as source:
        return yaml.safe_load(source)

class Patrick(commands.Bot):
    def __init__(self, logger: logging.Logger, config: dict):
        self.logger = logger
        self.config = config
        self.database = database.Connector()
        activity = discord.Activity(type=discord.ActivityType.playing, name="with Python")
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=',', case_insensitive=True, intents=intents, activity=activity)

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if message.content.startswith(self.command_prefix):
            if await util.process_custom_command(self, message):
                return
        await self.process_commands(message)

    async def on_ready(self):
        await self.database.connect()
        self.aiosession = ClientSession()
        await self.load_extensions()
        self.logger.info(f'Logged in as {self.user}')

    async def process_commands(self, message: discord.Message) -> None:
        ctx = await self.get_context(message)
        if ctx.command is not None:
            self.logger.info(f"User '{message.author}' ran command '{ctx.command.name}'")
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
                self.load_extension(f"cogs.{extension[:-3]}")
                status[extension] = "L"
            except Exception as e:
                errors.append(e)

        maxlen = max(len(str(extension)) for extension in status)
        for extension in status:
            self.logger.info(f" {extension.ljust(maxlen)} | {status[extension]}")
        self.logger.error(errors) if errors else self.logger.info("no errors during loading of extensions")

    async def reload_extensions(self):
        for extension in list(self.extensions):
            self.logger.info(f"Reloading extension {extension}")
            self.reload_extension(extension)

config = load_config()
logging_level = config.get("logging_level", "").upper()
if logging_level in ("DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"):
    logging.basicConfig(level=logging.getLevelName(logging_level))
else:
    print("Invalid logging level in config.yaml, defaulting to INFO")
    logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger('patrick')
logging.basicConfig(level=logging.INFO)
patrick: Patrick = Patrick(logger, config)

@patrick.command()
@commands.is_owner()
async def reload(ctx):
    m: discord.Message = await ctx.send("Reloading extensions...")
    await patrick.reload_extensions()
    await m.edit(content="Reloaded extensions")
    await m.delete(delay=5)
    await ctx.message.delete(delay=5)

patrick.run(TOKEN)
