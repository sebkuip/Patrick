import re
from os import getenv, listdir
from pathlib import Path
import logging

import discord
from discord.ext import commands
import yaml
from dotenv import load_dotenv

import database

logger: logging.Logger = logging.getLogger('patrick')
logging.basicConfig(level=logging.INFO)

load_dotenv(Path(__file__).parent / '.env')
TOKEN: str = getenv('TOKEN')

def load_config():
    with open(Path(__file__).parent / 'config.yaml', 'r') as source:
        return yaml.safe_load(source)

class Patrick(discord.Bot):
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        intents = discord.Intents.all()
        super().__init__(command_prefix=',', intents=intents)

    async def on_message(self, message: discord.Message):
        if message.author == client.user:
            return
        await self.process_commands(message)

    async def on_ready(self):
        await self.load_extensions()
        logger.info(f'Logged in as {self.user}')

    async def load_extensions(self):
        logger.info("Loading extensions")
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
                await bot.load_extension(f"cogs.{extension[:-3]}")
                status[extension] = "L"
            except Exception as e:
                errors.append(e)

        maxlen = max(len(str(extension)) for extension in status)
        for extension in status:
            print(f" {extension.ljust(maxlen)} | {status[extension]}")
        logger.error(errors) if errors else logger.info("no errors during loading of extensions")

def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    client = discord.Client(intents=intents)

    connector = database.Connector()

    config = load_config()
    gamechat_regex = re.compile(config['ingame_regex'])

    commands = [
        BasicCommand("ping", [
            "pong, I guess", "no, this is patrick", "*no, this is **patrick***", "# NO, THIS IS PATRICK"
        ]),
        ApplyCommand(),
        QuoteCommand(),
        XkcdCommand(),
        RemoveCommand(connector),
        DynamicHelpCommand(connector)
    ]

    commands.append(AddCommand(connector, [command.key for command in commands]))
    commands.append(HelpCommand(commands))

    def get_commands():
        return commands + [BasicCommand(command[0], command[1]) for command in connector.get_commands()]

    @client.event
    async def on_ready():
        logger.info(f'Logged in as {client.user}')

    @client.event
    async def on_message(message: Message):
        if message.author == client.user:
            return

        author = message.author
        content = message.content

        can_admin = config['staff_role'] in {role.id for role in author.roles}

        if message.channel.id == config['channels']['gamechat'] and author.bot:
            match = gamechat_regex.match(content)
            if not match:
                return
            can_admin = False
            author, content = match.groups()

        if content.startswith(","):
            content = content.removeprefix(",")
            try:
                command = [command for command in get_commands() if content.split()[0] == command.key][0]
            except IndexError:
                logger.info(f"User '{author}' attempted to run an unrecognized command: '{content}'")
                await message.reply("Unrecognized command :'(")
                return
            if command.is_admin and not can_admin:
                await message.reply("Unauthorized :'(")
                return
            try:
                logger.info(f"User '{author}' ran command '{content}'")
                await command.execute(message)
            except:  # This is a blanket catch but... yeah
                logger.exception(f"User '{author}' encountered an error running command '{content}'")
                await message.reply("Internal error :'(")

    client.run(token)


if __name__ == '__main__':
    patrick = Patrick()
    patrick.run(TOKEN)
