import re
from os import getenv
from pathlib import Path

import discord
import yaml
from discord import Message
from dotenv import load_dotenv
from loguru import logger

import database
from commands import BasicCommand, QuoteCommand, AddCommand, RemoveCommand, HelpCommand, DynamicHelpCommand, XkcdCommand

load_dotenv(Path(__file__).parent / '.env')
token = getenv('TOKEN')


def load_config():
    with open(Path(__file__).parent / 'config.yaml', 'r') as source:
        return yaml.safe_load(source)


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
    main()
