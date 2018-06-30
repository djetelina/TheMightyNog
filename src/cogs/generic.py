"""
Generic commands
"""
from discord.ext import commands


class Generic:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Says hello', brief='Says hello')
    async def hi(self, ctx: commands.Context):
        await ctx.send(f'Hello to you too {ctx.author.mention}')


def setup(bot):
    bot.add_cog(Generic(bot))
