"""
Commands related to ingame stuff
"""
from discord import Embed
from discord.ext import commands

from communication import scrollsguide


class Game:
    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot

    @commands.command(description="Get info about a scroll", brief="Get info about a scroll")
    async def scroll(self, ctx: commands.Context, *name: str):
        async with ctx.typing():
            try:
                scroll = await scrollsguide.get_scroll(' '.join(name))
            except scrollsguide.ScrollNotFound:
                await ctx.send("I couldn't find that scroll")
            except scrollsguide.MultipleScrollsFound as e:
                await ctx.send(str(e))
            else:
                embed = Embed(title=scroll.name, description=scroll.rarity)
                embed.set_thumbnail(url=scroll.image_url)
                embed.add_field(name='Cost', value=scroll.cost)
                type_ = scroll.kind
                if scroll.types:
                    type_ = f'{type_}: {scroll.types}'
                embed.add_field(name='Type', value=type_)
                if scroll.attack != '-' or scroll.countdown != '-' or scroll.health:
                    stats = f'\n<:attack:462355358229200916> {scroll.attack} | ' \
                            f'<:countdown:462355358057496577> {scroll.countdown} | ' \
                            f'<:health:462355358250434570> {scroll.health}'
                    embed.add_field(name='Stats', value=stats)
                if scroll.passive_rules:
                    embed.add_field(name='Passive rules', value=scroll.passive_rules)
                if scroll.description:
                    embed.add_field(name='Description', value=scroll.description)
                if scroll.flavor:
                    embed.set_footer(text=scroll.flavor)
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Game(bot))
