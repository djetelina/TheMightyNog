import asyncio
import logging
import time
from typing import Optional

from aiopg import sa
from aiopg.sa.result import ResultProxy, RowProxy
from discord.ext import commands
from prometheus_client import Summary, Counter


latency = Summary('command_latency_ms', 'Latency of a command in ms')
command_count = Counter('commands_invoked', 'How many times a command was invoked', ['channel'])
failed_command_count = Counter('failed_command_count', 'How many times a command failed unexpectedly')


class MightyNog(commands.Bot):

    def __init__(self, *args, **kwargs):
        self.__db_dsn = kwargs.pop('db')
        self.db_engine = None  # type: Optional[sa.Engine]
        asyncio.get_event_loop().run_until_complete(self.create_engine())
        super().__init__(*args, **kwargs)

    async def on_command(self, ctx: commands.context) -> None:
        ctx.start_time = time.time()
        channel = getattr(ctx.channel, "name", "PM")
        command_count.labels(channel).inc()
        logging.info(f'"{ctx.message.content}" by {ctx.author.name} @ {channel}')

    async def on_command_completion(self, ctx: commands.context) -> None:
        logging.info(f'"{ctx.message.content}" done')
        latency.observe((time.time() - ctx.start_time) * 1000)

    async def on_command_error(self, ctx: commands.context, exc: Exception) -> None:
        if isinstance(exc, commands.errors.CommandNotFound):
            # This might come back to bight me in the ass if the error string ever gets changed
            logging.info("Unknown command: {}".format(str(exc).split('"')[1]))
            await ctx.send("I don't know that command, try using `!help`")
        elif isinstance(exc, commands.errors.MissingRequiredArgument):
            await ctx.send("Not enough arguments provided, `!help` works for individual commands too")
        elif isinstance(exc, commands.errors.CheckFailure):
            await ctx.send(f"You can't do that {ctx.author.mention}!")
        else:
            logging.exception("Command failed", exc_info=exc)
            failed_command_count.inc()
        latency.observe((time.time() - ctx.start_time)*1000)

    async def create_engine(self):
        self.db_engine = await sa.create_engine(dsn=self.__db_dsn)
        async with self.db_engine.acquire() as conn:  # type: sa.SAConnection
            res = await conn.execute('SELECT NOW()')  # type: ResultProxy
            ret = await res.fetchone()  # type: RowProxy
            if ret is None:
                raise Exception("Couldn't connect to database")
        logging.info('Connected to database')
