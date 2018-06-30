"""
Commands for developers
"""
import logging

from discord.ext import commands

from settings import devs


class Dev:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx: commands.Context):
        return ctx.author.id in devs

    @commands.command(hidden=True)
    async def reload(self, ctx: commands.Context, module: str):
        async with ctx.typing():
            module = module.strip()
            module = f'cogs.{module}'
            try:
                self.bot.unload_extension(module)
                self.bot.load_extension(module)
            except Exception as _:
                logging.exception(f"Couldn't reload module: {module}")
            else:
                await ctx.send("Done!")

    @commands.command(hidden=True)
    async def load(self, ctx: commands.Context, module: str):
        async with ctx.typing():
            module = module.strip()
            module = f'cogs.{module}'
            try:
                self.bot.load_extension(module)
            except Exception as _:
                logging.exception(f"Couldn't load module: {module}")
            else:
                await ctx.send("Done!")

    @commands.command(hidden=True)
    async def unload(self, ctx: commands.Context, module: str):
        async with ctx.typing():
            module = module.strip()
            module = f'cogs.{module}'
            try:
                self.bot.unload_extension(module)
            except Exception as _:
                logging.exception(f"Couldn't unload module: {module}")
            else:
                await ctx.send("Done!")


def setup(bot):
    bot.add_cog(Dev(bot))
