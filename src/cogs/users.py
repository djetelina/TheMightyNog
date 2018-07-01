import sqlalchemy

from aiopg.sa import SAConnection
from discord.ext import commands

from db import tables
from mighty_nog import MightyNog


class User:
    def __init__(self, bot: MightyNog) -> None:
        self.bot = bot

    @commands.command(description='Register with the bot')
    async def register(self, ctx: commands.Context) -> None:
        async with ctx.typing():
            async with self.bot.db_engine.acquire() as conn:  # type: SAConnection
                exists_query = tables.users.select(tables.users.c.id_ == ctx.author.id)
                res = await conn.execute(exists_query)
                ret = await res.fetchone()
                if ret and ret.granted_permission is None:
                    await ctx.author.send("I need you to use the `!consent` command now")
                    return
                elif ret:
                    await ctx.author.send("You are already registered")
                    return

                insert_query = tables.users.insert().values(
                    id_=ctx.author.id
                )
                await conn.execute(insert_query)
                # TODO jinja/async template engine for these messages, starting to get annoying.
                await ctx.author.send("Thank you for registering!\n\n"
                                      "Before any of my registered only features start working, let me inform you "
                                      "that I will be storing personal information such as your username in my "
                                      "database and that this information will be considered public.\n\n"
                                      "At any time you can let the author - iScrE4m - know, that you'd like to "
                                      "view all stored information about you, or that you want it all to be forgotten "
                                      "(deleted, no going back).\n"
                                      "If you agree with all this, please respond with `!consent yes` and you'll be "
                                      "able to start enjoying the benefits of registered users. If you disagree, "
                                      "let me know with `!consent no` and I will forget that you ever asked.\n")

    @commands.command(description='For giving consent about personal information, process of registration')
    async def consent(self, ctx: commands.Context, consent: str) -> None:
        async with ctx.typing():
            consent = consent.lower()
            # This might be a bit ugly, we might quite possibly want to split this
            async with self.bot.db_engine.acquire() as conn:  # type: SAConnection
                status_query = tables.users.select(tables.users.c.id_ == ctx.author.id)
                res = await conn.execute(status_query)
                ret = await res.fetchone()
                if ret and ret.granted_permission:
                    await ctx.author.send("Thanks, but I already have your consent :)")
                    return
                elif ret is not None:
                    if consent.startswith('yes'):
                        await conn.execute(tables.users.update(tables.users.c.id_ == ctx.author.id).values(
                            granted_permission=sqlalchemy.text("now()")
                        ))
                        await ctx.author.send("Thanks, you're all set!")
                        return
                    elif consent.startswith('no'):
                        await conn.execute(tables.users.delete(tables.users.c.id_ == ctx.author.id))
                        await ctx.author.send("I'm sorry to hear that, I've forgotten your id. Feel free to message "
                                              "my author about your worries or opinions about personal data!")
                        return
                elif ret is None:
                    await ctx.author.send("Try using `!register` first")


def setup(bot):
    bot.add_cog(User(bot))
