import logging

import discord
from discord.ext import commands

from helpers import checks


class BotEvents:
    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot
        self.bot.event(self.on_message)
        self.bot.event(self.on_command)
        self.bot.command(hidden=True)(self.reload)
        self.bot.command(hidden=True)(self.load)
        self.bot.command(hidden=True)(self.unload)

    async def on_message(self, message: discord.Message):
        if message.author is self.bot.user:
            return

        await self.bot.process_commands(message)

    async def on_command(self, command: commands.Command, ctx: commands.context):
        if ctx.subcommand_passed is not None:
            cmd = f'{command} {ctx.subcommand_passed}'
        else:
            cmd = command.name

        try:
            logging.info(f"#{ctx.message.channel.name}: {ctx.message.author.name} called !{cmd}")
        except AttributeError:
            logging.info(f"PM: {ctx.message.author.name} called {cmd}")

    @checks.is_dev()
    async def reload(self, *, module: str):
        module = module.strip()
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as _:
            logging.exception(f"Couldn't reload module: {module}")
        else:
            await self.bot.say("Done!")

    @checks.is_dev()
    async def load(self, *, module: str):
        module = module.strip()
        try:
            self.bot.load_extension(module)
        except Exception as _:
            logging.exception(f"Couldn't load module: {module}")
        else:
            await self.bot.say("Done!")

    @checks.is_dev()
    async def unload(self, *, module: str):
        module = module.strip()
        try:
            self.bot.unload_extension(module)
        except Exception as _:
            logging.exception(f"Couldn't unload module: {module}")
        else:
            await self.bot.say("Done!")
