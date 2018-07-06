import logging
from typing import Optional, Union

from aiopg.sa import SAConnection
from discord.ext import commands

from communication.cbsapi import CBSAPI
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

    @commands.command(**commands_info.servers_rating)
    async def rating(self, ctx: commands.Context, player: str, server_name: str='ScrollsGuide'):
        async with ctx.typing():
            async with self.bot.db_engine.acquire() as conn:
                server = await self.__get_server_check_api(ctx, conn, server_name)
                await ctx.send("Not implemented yet, sorry :(")
                return

    @commands.command(**commands_info.servers_top)
    async def top(self, ctx: commands.Context, server_name: str='ScrollsGuide'):
        async with ctx.typing():
            async with self.bot.db_engine.acquire() as conn:
                server = await self.__get_server_check_api(ctx, conn, server_name)
                if server is None:
                    await ctx.send(f"I'm not aware of a server: {server_name}")
                    return
                elif server is False:
                    await ctx.send(f"Server {server_name} doesn't offer ratings api")
                    return
                else:
                    api = CBSAPI(server.cbsapi)
                    top_ten = await api.ranking()
                    # TODO again, templating is needed here.
                    resp = f"Top 10 @ {server_name}\n```"
                    rank = 1
                    for i, player in enumerate(top_ten, start=1):
                        if player['rating'] != top_ten[i - 2]['rating']:
                            rank = i
                        resp += f"{rank:2}. {player['name']:12} | {int(player['rating'])}"
                    resp += '```'
                    await ctx.send(resp)

    async def __get_server_check_api(self, ctx: commands.Context, conn: SAConnection, server_name: str) -> \
            Union[None, bool, BotServer]:
        servers = await BotServers.load_all(conn, ctx.guild)
        server = servers.get_by_name(server_name)
        if server is None:
            return None
        if not server.cbsapi:
            return False
        else:
            return server


def setup(bot):
    bot.add_cog(Servers(bot))
