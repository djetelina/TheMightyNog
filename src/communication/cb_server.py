import asyncio
import hashlib
import json
import logging
from typing import Any

from prometheus_client import Counter

SEPARATOR = b'\n\n'
PASSWORD_SALT = 'ScrollsClientSalt5438_'

message_received = Counter(
    'cb_message_received',
    "Counter of received messages from Caller's Bane server",
    ['message_type']
)


class CBServer:
    def __init__(self, address: str, port: int, username: str, password: str, reconnect: bool=True) -> None:
        self.address = address
        self.port = port
        self.username = username
        self.__password = password
        self.reconnect = reconnect
        self.reader = None  # type: Any
        self.writer = None  # type: Any
        self.connected = False
        self.handlers = {}  # type: dict

    async def connect(self) -> None:
        await self.__connect()
        await self.__login()
        self.connected = True
        await self.join_room('general-1')
        asyncio.ensure_future(self.__keep_alive())

    async def listen(self):
        while True:
            try:
                incoming_msg = await self.__receive()
            except asyncio.streams.IncompleteReadError:
                self.connected = False
                logging.error("Lost connection to Caller's Bane game server")
                if self.reconnect:
                    logging.info("Reconnecting to Caller's Bane game server in 120 seconds")
                    await asyncio.sleep(120)
                    await self.connect()
                    await self.__login()
                break
            else:
                await self.__handle_message(incoming_msg.pop('msg'), incoming_msg)

    async def join_room(self, room_name: str) -> None:
        await self.__send(dict(msg='RoomEnter', roomName=room_name))

    async def message_room(self, room_name: str, text: str) -> None:
        await self.__send(dict(msg='RoomChatMessage', text=text, roomName=room_name))

    async def __connect(self) -> None:
        msg_limit = 2 ** 32  # just to be safe, on connection fairly huge chunks are sent
        self.reader, self.writer = await asyncio.open_connection(self.address, self.port, limit=msg_limit)
        logging.info("Connected to Caller's Bane game server")

    async def __keep_alive(self) -> None:
        while self.connected:
            await asyncio.sleep(60)
            if self.connected:
                await self.__send(dict(msg='Ping'))

    async def __login(self) -> None:
        sha_auth_hash = hashlib.sha256()
        # Random string, who knows what this does
        sha_auth_hash.update(b'TheMightyNog')
        auth_hash = sha_auth_hash.hexdigest()

        await self.__send(dict(
            email=self.username,
            password=self.__encrypted_password,
            authHash=auth_hash,
            msg='FirstConnect'
        ))

        # Wait for ack from server
        while True:
            incoming_msg = await self.__receive()
            if incoming_msg.get('op') == 'FirstConnect' and incoming_msg.get('msg') == 'Ok':
                break

        logging.info("Logged in to Caller's Bane game server")

    @property
    def __encrypted_password(self) -> str:
        sha_password = hashlib.sha256()
        sha_password.update(str(PASSWORD_SALT + self.__password).encode('UTF-16LE'))
        return sha_password.hexdigest()

    async def __send(self, msg: dict) -> None:
        dumped_msg = json.dumps(msg).encode()
        self.writer.write(dumped_msg)
        await self.writer.drain()

    async def __receive(self) -> dict:
        server_msg = (await self.reader.readuntil(SEPARATOR)).decode()
        return json.loads(server_msg)

    async def __handle_message(self, message_type, data) -> None:
        message_received.labels(message_type).inc()
        func = self.handlers.get(message_type)
        if func is not None:
            await func(data)
