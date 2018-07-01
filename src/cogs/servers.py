from aiopg.sa import SAConnection
from discord.ext import commands

from db.objects import BotUser, BotServers
from helpers import commands_info


class Servers:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(**commands_info.servers_servers)
    async def servers(self, ctx: commands.Context):
        async with ctx.typing():
            async with self.bot.db_engine.acquire() as conn:
                if ctx.invoked_subcommand is None:
                    servers = await BotServers.load_all(conn)
                    await ctx.send(servers.printable)

    @servers.command(**commands_info.servers_publish)
    async def _publish(self, ctx: commands.Context, server_name: str, server_address: str):
        async with ctx.typing():
            async with self.bot.db_engine.acquire() as conn:  # type: SAConnection
                user = await BotUser.from_db(conn, ctx.author.id)
                if not user.registered:
                    await ctx.author.send(
                        "To publish a server you need to be registered first, use `!register` please!")
                    return
                await user.publish_server(conn, server_name, server_address)
                await ctx.author.send("Thanks, your server is now published! \n"
                                      "If you are running CSBPAPI, please let me know with "
                                      "`!server csbapi on`")


def setup(bot):
    bot.add_cog(Servers(bot))
