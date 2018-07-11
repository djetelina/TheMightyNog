import logging

from aiopg.sa import SAConnection
from discord.ext import commands

from communication.db.objects import BotUser, UnknownConsentReply
from helpers import commands_info
from mighty_nog import MightyNog


class User:
    def __init__(self, bot: MightyNog) -> None:
        self.bot = bot

    @commands.command(**commands_info.users_register)
    async def register(self, ctx: commands.Context) -> None:
        async with ctx.typing():
            async with self.bot.db_engine.acquire() as conn:  # type: SAConnection
                user = await BotUser.from_db(conn, ctx.author.id)
                if user.registering:
                    await ctx.author.send("I need you to use the `!consent` command now")
                    return
                elif user.registered:
                    await ctx.author.send("You are already registered")
                    return
                else:
                    await user.register(conn, ctx.author.id)
                    # TODO jinja/async template engine for these messages, starting to get annoying.
                    resp = self.bot.templating.get_template('register.md').render()
                    await ctx.author.send(resp)

    @commands.command(**commands_info.users_consent)
    async def consent(self, ctx: commands.Context, consent: str) -> None:
        async with ctx.typing():
            async with self.bot.db_engine.acquire() as conn:  # type: SAConnection
                user = await BotUser.from_db(conn, ctx.author.id)
                if user.registered:
                    await ctx.author.send("Thanks, but I already have your consent :)")
                    return
                elif user.registering:
                    try:
                        consented = await user.process_consent(conn, consent)
                    except UnknownConsentReply as _:
                        await ctx.author.send("This might be a bit awkward, but I don't know if that's a yes or no")
                        return
                    if consented:
                        await ctx.author.send("Thanks, you're all set!")
                        logging.info(f'{ctx.author.name} is now registered with their consent given!')
                        return
                    elif not consented:
                        await ctx.author.send("I'm sorry to hear that, I've forgotten your id. Feel free to message "
                                              "my author about your worries or opinions about personal data!")
                        return
                else:
                    await ctx.author.send("Try using `!register` first")


def setup(bot):
    bot.add_cog(User(bot))
