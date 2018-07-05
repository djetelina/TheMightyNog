import json

import aiohttp


class CBSAPI:
    def __init__(self, address: str):
        self.address = address

    async def ranking(self):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f'{self.address.rstrip("/")}/ranking') as resp:
                text = await resp.text()
                data = json.loads(text)
                # TODO check if status = OK
                top_ten = data['data'][:10]
                return top_ten
