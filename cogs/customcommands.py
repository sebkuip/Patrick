from discord import app_commands
from discord.ext import commands

from util import app_is_staff


class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def setup(bot):
        await bot.tree.sync()

    @app_commands.command(description="Add a custom command to the bot.")
    @app_is_staff()
    async def add(self, interaction, key: str, *, message: str):
        commands = self.bot.database.commands_cache
        if key in commands:
            await ctx.send(f"Command `{key}` already exists. Use `addresponse` to add another response.")
            return
        await self.bot.database.add_command(key, message)
        await interaction.response.send_message(f"Command `{key}` added.")

    @app_commands.command(description="Add a response to an already existing command.")
    @app_is_staff()
    async def add_response(self, interaction, key: str, *, message: str):
        if key not in self.bot.database.commands_cache:
            await interaction.response.send_message(f"Command `{key}` does not exist.", ephemeral=True)
            return
        self.bot.database.add_command_response(key, message)
        await interaction.response.send_message(f"Response added to command `{key}`.")

    @add_response.autocomplete("key")
    async def autocomplete_key(self, interaction, current: str):
        commands = self.bot.database.commands_cache
        return [app_commands.Choice(name=key, value=key) for key in commands if current.lower() in key.lower()]

    @app_commands.command(description="Remove a custom command from the bot.")
    @app_is_staff()
    async def remove(self, interaction, key: str):
        if key not in self.bot.database.commands_cache:
            await interaction.response.send_message(f"Command `{key}` does not exist.", ephemeral=True)
            return
        await self.bot.database.remove_command(key)
        await interaction.response.send_message(f"Command `{key}` removed.")

    @remove.autocomplete("key")
    async def autocomplete_key(self, interaction, current: str):
        commands = self.bot.database.commands_cache
        return [app_commands.Choice(name=key, value=key) for key in commands if current.lower() in key.lower()]
    
    @app_commands.command(description="Remove a response from an already existing command.")
    @app_is_staff()
    async def remove_response(self, interaction, key: str, *, message: str):
        if key not in self.bot.database.commands_cache:
            await interaction.response.send_message(f"Command `{key}` does not exist.", ephemeral=True)
            return
        if message not in self.bot.database.commands_cache[key]:
            await interaction.response.send_message(f"Response `{message}` does not exist for command `{key}`.", ephemeral=True)
            return
        await self.bot.database.remove_command_response(key, message)
        await interaction.response.send_message(f"Response `{message}` removed from command `{key}`.")

    @remove_response.autocomplete("key")
    async def autocomplete_key(self, interaction, current: str):
        commands = self.bot.database.commands_cache
        return [app_commands.Choice(name=key, value=key) for key in commands if current.lower() in key.lower()]
    
    @remove_response.autocomplete("message")
    async def autocomplete_message(self, interaction, current: str):
        key = interaction.namespace.key
        if key not in self.bot.database.commands_cache:
            return []
        messages = self.bot.database.commands_cache[key]
        return [app_commands.Choice(name=message, value=message) for message in messages if current.lower() in message.lower()]

    @comands.command(help="Add a response to an existing custom command.")
    @is_staff()
    async def addresponse(self, ctx, key: str, *, message: str):
        commands = await get_custom_commands(self.bot)
        if key not in commands:
            await ctx.send(f"Command `{key}` does not exist. Use `addcommand` to add it.")
            return
        await self.bot.database.add_response(key, message)
        await ctx.send(f"Response added to command `{key}`.")

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
