import logging

import discord
from discord.ext import commands


class MightyNog(commands.Bot):

    async def on_message(self, message: discord.Message) -> None:
        if message.author is self.user:
            return
        await self.process_commands(message)

    async def on_command(self, ctx: commands.context) -> None:
        logging.info(f'"{ctx.message.content}" by {ctx.author.name} @ #{ctx.channel.name} ')

    async def on_command_completion(self, ctx: commands.context) -> None:
        logging.info(f'"{ctx.message.content}" done')

    async def on_command_error(self, ctx: commands.context, exc: Exception) -> None:
        if isinstance(exc, commands.errors.CommandNotFound):
            # This might come back to bight me in the ass if the error string ever gets changed
            logging.info("Unknown command: {}".format(str(exc).split('"')[1]))
            await ctx.send("I don't know that command, try using `!help`")
        if isinstance(exc, commands.errors.MissingRequiredArgument):
            pass
        else:
            logging.exception("Command failed", exc_info=exc)
