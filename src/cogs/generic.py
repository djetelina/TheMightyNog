"""
Generic commands
"""
from discord.ext import commands

from helpers import commands_info


class Generic:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Says hello', brief='Says hello')
    async def hi(self, ctx: commands.Context):
        await ctx.send(f'Hello to you too {ctx.author.mention}')

    @commands.command(**commands_info.generic_patreon)
    async def patreon(self, ctx: commands.Context):
        await ctx.send('Scrollsguide patreon page: https://www.patreon.com/scrollsguide')


def setup(bot):
    bot.add_cog(Generic(bot))
