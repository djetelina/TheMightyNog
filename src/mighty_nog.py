import asyncio
import hashlib
import json
import logging
import pathlib
import time
from typing import Optional

from aiopg import sa
from aiopg.sa.result import ResultProxy, RowProxy
from discord import Message
from discord.ext import commands
from jinja2 import FileSystemLoader, Environment
from prometheus_client import Summary, Counter

latency = Summary('command_latency_ms', 'Latency of a command in ms')
command_count = Counter('commands_invoked', 'How many times a command was invoked', ['guild', 'channel', 'command_name'])
failed_command_count = Counter('failed_command_count', 'How many times a command failed unexpectedly')
sg_chat = Counter('sg_chat', 'How many times a message was relayed to and from sg chat', ['destination'])


class MightyNog(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.__db_dsn = kwargs.pop('db')
        self.__sg_password = kwargs.pop('sg_password')
        self.db_engine = None  # type: Optional[sa.Engine]
        asyncio.get_event_loop().run_until_complete(self.create_engine())
        self.templating = self.__init_templating()
        self.__sg_connected = False  # type: bool
        super().__init__(*args, **kwargs)

    async def on_command(self, ctx: commands.Context) -> None:
        ctx.start_time = time.time()
        channel = getattr(ctx.channel, "name", "PM")
        guild = getattr(ctx.guild, "name", "PM")
        command = f'{ctx.command.name} {ctx.invoked_subcommand.name}' if ctx.invoked_subcommand else ctx.command.name
        command_count.labels(guild, channel, command).inc()
        logging.info(f'"{ctx.message.content}" by {ctx.author.name} @ {channel}')

    async def on_command_completion(self, ctx: commands.context) -> None:
        logging.info(f'"{ctx.message.content}" done')
        latency.observe((time.time() - ctx.start_time) * 1000)

    async def on_command_error(self, ctx: commands.Context, exc: Exception) -> None:
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

    async def on_message(self, message: Message):
        if message.channel.id == 487693801373040640 and message.author.id != self.user.id:
            send_msg = {
                'msg': 'RoomChatMessage',
                'text': f'{message.author.display_name}@Nognest: {message.content}',
                'roomName': 'general-1'
            }
            self.sg_game_writer.write(json.dumps(send_msg).encode())
            sg_chat.labels('ScrollsGuide').inc()

    async def on_ready(self):
        asyncio.ensure_future(self.__listen_to_sg_chat())

    async def create_engine(self):
        self.db_engine = await sa.create_engine(dsn=self.__db_dsn)
        async with self.db_engine.acquire() as conn:  # type: sa.SAConnection
            res = await conn.execute('SELECT NOW()')  # type: ResultProxy
            ret = await res.fetchone()  # type: RowProxy
            if ret is None:
                raise Exception("Couldn't connect to database")
        logging.info('Connected to database')

    def __init_templating(self) -> Environment:
        loader = FileSystemLoader(searchpath=str(pathlib.Path(__file__).resolve().parent.parent / 'templates'))
        template_env = Environment(loader=loader)
        return template_env

    async def __listen_to_sg_chat(self) -> None:
        # TODO this should be split somewhere else and abstracted etc but I just want it done
        msg_limit = 2 ** 32  # just to be safe, on connection fairly huge chunks are sent
        reader, writer = await asyncio.open_connection('play.scrollsguide.com', 8081, limit=msg_limit)
        self.sg_game_writer = writer
        logging.info("Connected to SG game server")

        # Hash our password
        salt = 'ScrollsClientSalt5438_'
        sha_password = hashlib.sha256()
        sha_password.update(str(salt + self.__sg_password).encode('UTF-16LE'))
        password = sha_password.hexdigest()
        del sha_password

        sha_auth_hash = hashlib.sha256()
        sha_auth_hash.update(b'TheMightyNog')
        auth_hash = sha_auth_hash.hexdigest()

        login_msg = json.dumps({
            'email': 'TheMightyNog',
            'password': password,
            'authHash': auth_hash,
            'msg': 'FirstConnect'
        }).encode()

        writer.write(login_msg)
        while True:
            incoming_msg = json.loads((await reader.readuntil(b'\n\n')).decode())
            if incoming_msg.get('op') == 'FirstConnect' and incoming_msg.get('msg') == 'Ok':
                break
        logging.info("Logged in to SG game server")

        enter_general_msg = json.dumps({
            'msg': 'RoomEnter',
            'roomName': 'general-1'
        }).encode()
        writer.write(enter_general_msg)

        gen_1 = self.get_channel(487693801373040640)

        asyncio.ensure_future(self.__keep_pinging_sg(writer))
        while True:
            try:
                incoming_msg = await reader.readuntil(b'\n\n')
            except asyncio.streams.IncompleteReadError:
                self.__sg_connected = False
                logging.exception("Connection to SG game server interrupted :(")
                break
            else:
                incoming_json = json.loads(incoming_msg.decode())
                if incoming_json.get('msg') == 'RoomChatMessage' and incoming_json['from'] not in ('TheMightyNog', 'System'):
                    await gen_1.send(f"**{incoming_json['from']}:** {incoming_json['text']}")
                    sg_chat.labels('Discord').inc()

    async def __keep_pinging_sg(self, writer: asyncio.StreamWriter):
        """So we don't disconnect"""
        while self.__sg_connected:
            asyncio.sleep(5)
            if self.__sg_connected:
                writer.write(json.dumps({'msg': 'Ping'}).encode())
