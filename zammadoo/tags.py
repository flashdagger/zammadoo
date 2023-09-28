#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Union

if TYPE_CHECKING:
    from .client import Client


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
        items = self.client.get(self.endpoint)
        assert isinstance(items, list)
        cache.update((info["name"], info) for info in items)
        return list(cache.keys())

    def create(self, name: str):
        self.client.post(self.endpoint, params={"name": name})

    def remove(self, name_or_tid: Union[str, int]):
        if isinstance(name_or_tid, str):
            name_or_tid = self._map[name_or_tid]["id"]
        self.client.delete(f"{self.endpoint}/{name_or_tid}")

    def add_to_ticket(self, name: str, tid: int):
        params = {"item": name, "object": "Ticket", "o_id": tid}
        return self.client.post("tags/add", params=params)

    def remove_from_ticket(self, name: str, tid: int):
        params = {"item": name, "object": "Ticket", "o_id": tid}
        return self.client.delete("tags/remove", params=params)

    def search(self, term: str) -> List[str]:
        items = self.client.get("tag_search", params={"term": term})
        assert isinstance(items, list)
        found = []
        for info in items:
            name = info["name"] = info.pop("value")
            self._map.setdefault(name, info)
            found.append(name)

        return found

    def by_ticket(self, tid: int) -> List[str]:
        items = self.client.get("tags", params={"object": "Ticket", "o_id": tid})
        assert isinstance(items, dict)
        return items.get("tags", [])
