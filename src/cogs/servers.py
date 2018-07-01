from aiopg.sa import SAConnection
from discord.ext import commands

from db.objects import BotUser, BotServers, BotServer
from helpers import commands_info


class Servers:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(**commands_info.servers_servers)
    async def servers(self, ctx: commands.Context):
        async with ctx.typing():
            async with self.bot.db_engine.acquire() as conn:
                if ctx.invoked_subcommand is None:
                    servers = await BotServers.load_all(conn, ctx.guild)
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
                                      "If you are running CBSAPI, please let me know with "
                                      "`!servers cbsapi <your_server_name> on`")

    @servers.command(**commands_info.servers_cbsapi)
    async def _cbsapi(self, ctx: commands.Context, server_name: str, api_address: str):
        falsy_args = {'off', 'no', 'disabled', 'disable'}
        desired_state = None if api_address in falsy_args else api_address
        async with ctx.typing():
            async with self.bot.db_engine.acquire() as conn:
                server = await BotServer.from_db(conn, server_name)
                if server is None:
                    await ctx.author.send("I don't know that server")
                    return
                if server.owner != ctx.author.id:
                    await ctx.author.send("That is not your server!")
                    return
                if server is None:
                    await ctx.author.send(f"Unknown server {server_name}, try `!help servers publish`")
                    return
                if desired_state == server.cbsapi:
                    await ctx.author.send(f"The state of your cbsapi is already set to {str(desired_state)}")
                    return
                else:
                    await server.set_cbsapi(conn, desired_state)
                    await ctx.author.send(f"Your server now has cbsapi: {str(desired_state)}")


def setup(bot):
    bot.add_cog(Servers(bot))
