"""
Commands related to ingame stuff
"""
from discord.ext import commands

from communication import scrollsguide


class Game:
    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot

    @commands.command(decsription="Get info about a scroll", brief="Get info about a scroll")
    async def scroll(self, ctx: commands.Context, *name: str):
        async with ctx.typing():
            name = [part.capitalize() for part in name]
            try:
                scroll = await scrollsguide.get_scroll(' '.join(name))
            except scrollsguide.ScrollNotFound:
                await ctx.send("I couldn't find that scroll")
            except scrollsguide.MultipleScrollsFound as e:
                await ctx.send(str(e))
            else:
                await ctx.send(scroll.printable)


def setup(bot):
    bot.add_cog(Game(bot))
