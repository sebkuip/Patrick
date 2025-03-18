import discord
from discord.ext import commands

import traceback

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # This is the bot instance, it lets us interact with most things

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, FileNotFoundError):
            return
        elif isinstance(error, commands.NotOwner) or isinstance(error, commands.MissingPermissions)::
            await ctx.send("You do not have permissions for this command.")
            return
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Member not found.")
            return
        elif isinstance(error, commands.BadArgument):
            await ctx.send("The argument you gave is invalid/cannot be processed.")
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"Command usage: `,{ctx.command.name} {ctx.command.signature}`"
            )
            return
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found.")
            return
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Bot does not have permissions for this command.")
            return
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("This command is disabled.")
            return
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send("This command can only be used in DMs.")
            return
        else:
            await ctx.send("An unknown error occurred while processing the command.")
            traceback.print_tb(error.__traceback__)
            self.bot.logger.error(error)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))