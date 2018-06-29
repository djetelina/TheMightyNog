from discord.ext import commands

from communication import scrollsguide


class Game:
    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot

    @commands.command(decsription="Get info about a scroll")
    async def scroll(self, *name: str):
        name = [part.capitalize() for part in name]
        try:
            scroll = await scrollsguide.get_scroll(' '.join(name))
        except scrollsguide.ScrollNotFound:
            await self.bot.say("I couldn't find that scroll")
        else:
            await self.bot.say(scroll.printable)


def setup(bot):
    bot.add_cog(Game(bot))
