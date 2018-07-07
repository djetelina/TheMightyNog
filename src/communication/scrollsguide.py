"""
Library for communicating with the scrollsguide API(s)
"""
import aiohttp
import json
from urllib.parse import quote_plus
from typing import Any, Dict, Tuple, Type
from fuzzywuzzy import fuzz

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

class Scroll:
    """Wrapper class for Scroll information coming from the API"""

    _scrolls_db = None
    _scrolls_names = None

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

    @classmethod
    async def load_scrolls(cls: Type['Scroll']) -> None:
        """Gets information about scrolls"""
        async with aiohttp.ClientSession() as s:
            async with s.get('http://a.scrollsguide.com/scrolls') as resp:
                text = await resp.text()
                data = json.loads(text)
                cls._scrolls_db = {}
                cls._scrolls_names = {}
                for scroll_data in data.get('data', []):
                    scroll = Scroll(scroll_data)
                    cls._scrolls_db[scroll._id] = scroll
                    cls._scrolls_names[scroll.name.lower()] = scroll._id

    @classmethod
    async def get(cls: Type['Scroll'], query: str, threshold: float = 0.7) -> 'Scroll':
        query = query.lower()
        if cls._scrolls_db is None or cls._scrolls_names is None:
            # Lazy initialization
            await cls.load_scrolls()
        if query in cls._scrolls_names.keys():
            return cls._scrolls_db[cls._scrolls_names[query]]
        else:
            # do a fuzzy search
            name_scores = {}
            for scroll_name, id in cls._scrolls_names.items():
                # 0.995 and 1.000 are really the same for grouping
                score = round(fuzz.partial_ratio(query, scroll_name), 2)
                if score >= threshold:
                    name_scores[id] = score
                # Only select top items from the list
                max_score = max(name_scores.values())
                closest_items = [id for id, score in name_scores.items() if score == max_score]
                if len(closest_items) == 1:
                    return cls._scrolls_db[closest_items[0]]
                elif len(closest_items) > 1:
                    raise MultipleScrollsFound([cls._scrolls_db[id] for id in closest_items], query)
                else:
                    raise ScrollNotFound
