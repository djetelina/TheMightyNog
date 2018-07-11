import aiohttp
import json
from urllib.parse import urlencode


class CBSAPIException(Exception):
    pass


class PlayerNotFound(CBSAPIException):
    pass


class CBSAPI:
    def __init__(self, address: str) -> None:
        self.address = address.rstrip("/")

    async def ranking(self):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f'{self.address}/ranking') as resp:
                text = await resp.text()
                data = json.loads(text)
                # TODO check if status = OK
                top_ten = data['data'][:10]
                return top_ten

    async def player(self, name, avatar=False, unlocks=False, collection=False, games=False):
        url = f'{self.address}/player/{name}'
        filters = []
        if avatar:
            filters.append(('filter', 'avatar'))
        if unlocks:
            filters.append(('filter', 'unlocks'))
        if collection:
            filters.append(('filter', 'collection'))
        if games:
            filters.append(('filter', 'games'))
        filters = urlencode(filters)
        if filters:
            url += f'?{filters}'
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as resp:
                text = await resp.text()
                json_data = json.loads(text)
                if json_data['status'] == 'OK':
                    return json_data['data']
                elif json_data['description'] == 'Player not found':
                    raise PlayerNotFound
                else:
                    raise CBSAPIException(json_data['description'])
