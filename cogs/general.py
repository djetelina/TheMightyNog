from discord.ext import commands


class General:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description='test', brief='test')
    async def hi(self, ctx):
        await self.bot.say(f'Hello to you too {ctx.message.author.mention}')


def setup(bot):
    bot.add_cog(General(bot))
