#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Union, cast

from .utils import StringKeyDict

if TYPE_CHECKING:
    from .client import Client


ItemDict = Dict[str, List[str]]
ItemList = List[StringKeyDict]


class Tags:
    def __init__(self, client: "Client"):
        self.client = client
        self._map: Dict[str, Dict[str, Any]] = {}
        self.endpoint = "tag_list"

    def __repr__(self):
        url = f"{self.client.url}/{self.endpoint}"
        return f"<{self.__class__.__qualname__} {url!r}>"

    def __iter__(self) -> Iterable[str]:
        yield from self._map.keys()

    def __getitem__(self, item) -> Dict[str, Any]:
        return self._map[item]

    def all(self) -> List[str]:
        cache = self._map
        cache.clear()
        items = cast(ItemList, self.client.get(self.endpoint))
        cache.update((info.pop("name"), info) for info in items)
        return list(cache.keys())

    def search(self, term: str) -> List[str]:
        items = cast(ItemList, self.client.get("tag_search", params={"term": term}))

        found = []
        for info in items:
            name = info.pop("value")
            self._map.setdefault(name, info)
            found.append(name)

        return found

    def create(self, name: str):
        self.client.post(self.endpoint, json={"name": name})

    def remove(self, name_or_tid: Union[str, int]):
        if isinstance(name_or_tid, str):
            name_or_tid = self._map[name_or_tid]["id"]
        self.client.delete(f"{self.endpoint}/{name_or_tid}")

    def rename(self, name_or_tid: Union[str, int], new_name: str):
        if isinstance(name_or_tid, str):
            name_or_tid = self._map[name_or_tid]["id"]
        self.client.put(f"{self.endpoint}/{name_or_tid}", json={"name": new_name})

    def add_to_ticket(self, tid: int, *names: str):
        for name in names:
            params = {"item": name, "object": "Ticket", "o_id": tid}
            self.client.post("tags/add", json=params)

    def remove_from_ticket(self, tid: int, *names: str):
        for name in names:
            params = {"item": name, "object": "Ticket", "o_id": tid}
            self.client.delete("tags/remove", json=params)

    def by_ticket(self, tid: int) -> List[str]:
        items = cast(
            ItemDict, self.client.get("tags", params={"object": "Ticket", "o_id": tid})
        )
        return items.get("tags", [])
