"""
Generic commands
"""
from discord.ext import commands


class Generic:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description='Says hello', brief='Says hello')
    async def hi(self, ctx):
        await self.bot.say(f'Hello to you too {ctx.message.author.mention}')


def setup(bot):
    bot.add_cog(Generic(bot))
