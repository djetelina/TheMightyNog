from typing import List

import sqlalchemy
from aiopg.sa import SAConnection
from aiopg.sa.result import RowProxy

from db import tables


class BotServers:
    def __init__(self, servers: List['BotServer']):
        self.servers = servers

    @classmethod
    async def load_all(cls, conn: SAConnection) -> 'BotServers':
        servers = list()
        res = await conn.execute(tables.servers.select())
        for row in await res.fetchall():
            servers.append(await BotServer.from_row_proxy(row))
        return cls(servers)

    @property
    def printable(self) -> str:
        servers = '\n'.join(server.printable for server in self.servers)
        if not servers:
            return "No servers yet!"
        return f'```\n' \
               f'{servers}\n' \
               f'```'


class BotServer:
    def __init__(self, name: str, address: str, owner: int, csbapi=False):
        self._name = name
        self._address = address
        self._owner = owner
        self.csbapi = csbapi

    @classmethod
    async def publish(cls, conn: SAConnection, name: str, address: str, owner: int) -> 'BotServer':
        await conn.execute(tables.servers.insert().values(
            name=name,
            address=address,
            owner=owner
        ))
        return cls(name, address, owner)

    @classmethod
    async def from_row_proxy(cls, row: RowProxy) -> 'BotServer':
        return cls(name=row.name, address=row.address, owner=row.owner)

    @property
    def printable(self) -> str:
        # TODO owner
        return f"{self._name} # {self._address}"


class BotUser:
    def __init__(self, *args, **kwargs):
        self._id_ = kwargs.pop('id_', None)
        self._granted_permission = kwargs.pop('granted_permission', None)

    @classmethod
    async def from_db(cls, conn: SAConnection, discord_id: int) -> 'BotUser':
        query = tables.users.select(tables.users.c.id_ == discord_id)
        res = await conn.execute(query)
        ret = await res.fetchone()
        if ret is None:
            return cls()
        else:
            return cls(id_=ret.id_, granted_permission=ret.granted_permission)

    @property
    def id_(self) -> int:
        return self._id_

    @property
    def registered(self) -> bool:
        return True if self.id_ is not None and self._granted_permission is not None else False

    @property
    def registering(self) -> bool:
        return True if self.id_ is not None and self._granted_permission is None else False

    async def register(self, conn: SAConnection) -> None:
        """Begins the process of registration, requires user GDPR consent to finish"""
        insert_query = tables.users.insert().values(
            id_=self.id_
        )
        await conn.execute(insert_query)

    async def process_consent(self, conn: SAConnection, consent: str) -> bool:
        """
        Processes the argument to !consent, updates the database accordingly and returns boolean
        so that the caller might know how to reply to user

        :param conn:                    Connection to database
        :param consent:                 Argument passed by the user
        :return:                        True if the user agreed, False if he disagreed
        :raises UnknownConsentReply:    If the argument was not recognized
        """
        consent = consent.strip().lower()
        if consent.startswith('yes'):
            await conn.execute(tables.users.update(tables.users.c.id_ == self._id_).values(
                granted_permission=sqlalchemy.text("now()")
            ))
            return True
        elif consent.startswith('no'):
            await self.delete(conn)
            return False
        else:
            raise UnknownConsentReply(consent)

    async def delete(self, conn: SAConnection):
        """Completely deletes any trace of the user from the database"""
        await conn.execute(tables.users.delete(tables.users.c.id_ == self._id_))

    async def publish_server(self, conn: SAConnection, server_name: str, server_address: str) -> None:
        await BotServer.publish(conn, server_name, server_address, self.id_)


class UserException(Exception):
    pass


class UnknownConsentReply(UserException):
    pass