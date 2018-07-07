"""
Library for communicating with the scrollsguide API(s)
"""
import aiohttp
import json
from urllib.parse import quote_plus
from typing import Dict, Tuple

class Scroll:
    """Wrapper class for Scroll information coming from the API"""
    def __init__(self, json_data: dict) -> None:
        self._id = json_data['id']
        self._name = json_data['name']
        self._description = json_data['description']
        self._kind = json_data['kind']
        self._types = json_data['types']
        self._growth_cost = json_data['costgrowth']
        self._order_cost = json_data['costorder']
        self._energy_cost = json_data['costenergy']
        self._decay_cost = json_data['costdecay']
        self._attack = json_data['ap']
        self._countdown = json_data['ac']
        self._health = json_data['hp']
        self._flavor = json_data['flavor']
        self._rarity = json_data['rarity']
        self._set = json_data['set']
        self._passive_rules = json_data.get('passiverules', [])
        self._abilities = json_data.get('abilities', [])

    @property
    def name(self) -> str:
        return self._name

    @property
    def image_url(self) -> str:
        return f'https://a.scrollsguide.com/image/screen?name={quote_plus(self.name)}&size=small'

    @property
    def cost(self) -> str:
        if self._growth_cost:
            return f'<:Growth:320829951534170113> {self._growth_cost}'
        if self._order_cost:
            return f'<:Order:320830133801975808> {self._order_cost}'
        if self._decay_cost:
            return f'<:Decay:320829724085583874> {self._decay_cost}'
        if self._energy_cost:
            return f'<:Energy:320830049039417344> {self._energy_cost}'

    @property
    def attack(self) -> str:
        return '-' if not self._attack else self._attack

    @property
    def countdown(self) -> str:
        return '-' if self._countdown < 1 else self._countdown

    @property
    def health(self) -> str:
        return self._health

    @property
    def rarity(self) -> str:
        rarities = {
            0: 'Common',
            1: 'Uncommon',
            2: 'Rare'
        }
        return rarities[self._rarity]

    @property
    def description(self) -> str:
        return self._description.replace('<', '').replace('>', '').replace('\\n', '\n').replace('[', '').replace(']', '')

    @property
    def flavor(self) -> str:
        return self._flavor.lstrip('\\n').replace('\\n', '\n')

    @property
    def passive_rules(self) -> str:
        return '; '.join([rule['name'].replace('[', '').replace(']', '') for rule in self._passive_rules])

    @property
    def types(self) -> str:
        return self._types.replace(',', ', ')

    @property
    def kind(self) -> str:
        return self._kind.capitalize()


class ScrollNotFound(Exception):
    pass


class MultipleScrollsFound(Exception):
    def __init__(self, scrolls, search_term):
        self.scrolls = [scroll['name'] for scroll in scrolls]
        self.search_term = search_term

    def __str__(self):
        if len(self.scrolls) > 5:
            return f"Too many scrolls start with {self.search_term}"
        return f'Multiple scrolls starting with {self.search_term}: {", ".join(self.scrolls)}'


async def get_scrolls() -> Tuple[Dict[str, Scroll], Dict[str, str]]:
    """Gets information about scrolls"""
    async with aiohttp.ClientSession() as s:
        # I'm sorry for fetching all of them, but the only limiting param is Id and I don't have the dict for that yet
        async with s.get('http://a.scrollsguide.com/scrolls') as resp:
            text = await resp.text()
            data = json.loads(text)

            scrolls = {}
            names   = {}
            for scroll_data in data.get('data', []):
                scroll = Scroll(scroll_data)
                scrolls[scroll._id] = Scroll
                names[scroll.name.lower()] = scroll._id
            return scrolls, names


def get_scroll(query: str, db: Dict[str, Scroll] = None, names: Dict[str, str] = None) -> Scroll:
    if db is None or names is None:
        db, names = get_scrolls()
    if query.lower() in names.keys():
        return db[names[query]]
    else:
        matches = [db[id] for scroll_name, id in names.items() if scroll_name.startswith(query)]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise MultipleScrollsFound(matches, query)
        else:
            raise ScrollNotFound