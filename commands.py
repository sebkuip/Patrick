import json
import random
from abc import ABC, abstractmethod

import requests
from discord import Message, Embed


class Command(ABC):
    def __init__(self, key):
        self.key = key
        self.is_admin = False

    @abstractmethod
    def execute(self, message: Message):
        pass


class BasicCommand(Command):
    def __init__(self, key, response):
        super().__init__(key)
        self.response = response

    async def execute(self, message: Message):
        if isinstance(self.response, list):
            to_send = random.choice(self.response)
        else:
            to_send = self.response
        await message.reply(to_send)


class HelpCommand(Command):
    def __init__(self, commands):
        super().__init__("help")
        self.commands = commands

    async def execute(self, message: Message):
        await message.reply(f"All commands: {', '.join([comm.key for comm in self.commands])}")


class DynamicHelpCommand(Command):
    def __init__(self, connector):
        super().__init__("dynamichelp")
        self.connector = connector

    async def execute(self, message: Message):
        await message.reply(f"Dynamic commands: {', '.join(comm[0] for comm in self.connector.get_commands())}")


class AddCommand(Command):
    def __init__(self, connector, existing_commands):
        super().__init__("add")
        self.is_admin = True
        self.connector = connector
        self.existing_commands = existing_commands

    async def execute(self, message: Message):
        parts = message.content.split()
        if len(parts) < 3:
            await message.reply("Not enough arguments! Please provide {add} {key} {message}")
            return
        key = parts[1]  # [0] is $add, [1] is the intended command key
        if self.connector.get_command(key) or key in self.existing_commands:
            await message.reply("Error! Command already exists.")
            return
        message_content = " ".join(parts[2:])  # [2:] is the rest of the message
        self.connector.add_command(key, message_content)
        await message.reply("Added!")


class RemoveCommand(Command):
    def __init__(self, connector):
        super().__init__("remove")
        self.is_admin = True
        self.connector = connector

    async def execute(self, message: Message):
        parts = message.content.split()
        if len(parts) < 2:
            await message.reply("Not enough arguments! Please provide {add} {key} {message}")
            return
        key = parts[1]
        if not self.connector.get_command(key):
            await message.reply("Command does not exist!")
            return
        self.connector.remove_command(key)
        await message.reply(f"Command '{key}' removed.")


class XkcdCommand(Command):
    def __init__(self):
        super().__init__("xkcd")

    @staticmethod
    def get_xkcd(num=0):
        to_insert = f"{num}/" if num > 0 else ""
        xkcd_url = f"https://xkcd.com/{to_insert}info.0.json"
        return requests.get(xkcd_url).json()

    @staticmethod
    def random_xkcd():
        newest_xkcd = XkcdCommand.get_xkcd(0)["num"]
        random_num = random.randint(0, newest_xkcd)
        return XkcdCommand.get_xkcd(random_num)

    async def execute(self, message: Message):
        prompt = message.content.split()
        xkcd_data = None
        if len(prompt) == 1:
            xkcd_data = XkcdCommand.random_xkcd()
        else:
            try:
                xkcd_data = XkcdCommand.get_xkcd(int(prompt[1]))
            except ValueError:
                await message.reply("The xkcd you provided is not a number.")
                return
        embed = Embed(
            title=xkcd_data["title"],
            description=xkcd_data["alt"],
            url=f"https://xkcd.com/{xkcd_data['num']}/"
        )
        embed.set_image(url=xkcd_data['img'])
        embed.set_footer(text=f"{xkcd_data['num']} ({xkcd_data['month']}/{xkcd_data['day']}/{xkcd_data['year']})")
        await message.reply(embed=embed)


class QuoteCommand(Command):
    def __init__(self):
        super().__init__("quote")

    async def execute(self, message: Message):
        quote = requests.get("https://zenquotes.io/api/random/")
        if quote.status_code != 200:
            raise ValueError
        data = json.loads(quote.text)
        await message.reply(f"\"{data[0]['q']}\" - {data[0]['a']}")
