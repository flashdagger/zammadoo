#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Union

if TYPE_CHECKING:
    from .client import Client
    from .types import StringKeyDict


class Tags:
    def __init__(self, client: "Client"):
        self.client = client
        self._map: Dict[str, Dict[str, Any]] = {}
        self.endpoint = "tag_list"

    def __repr__(self):
        url = f"{self.client.url}/{self.endpoint}"
        return f"<{self.__class__.__qualname__} {url!r}>"

    def __iter__(self) -> Iterable["StringKeyDict"]:
        self._reload()
        yield from self._map.values()

    def _reload(self) -> None:
        cache = self._map
        cache.clear()
        cache.update((info["name"], info) for info in self.client.get(self.endpoint))

    def as_list(self) -> List[str]:
        self._reload()
        return list(self._map.keys())

    def search(self, term: str) -> List[str]:
        items = self.client.get("tag_search", params={"term": term})

        for info in items:
            name = info.pop("value")
            info.update((("name", name), ("count", None)))
            self._map.setdefault(name, info)

        return list(info["name"] for info in items)

    def create(self, name: str):
        self.client.post(self.endpoint, json={"name": name})

    def delete(self, name_or_tid: Union[str, int]):
        if isinstance(name_or_tid, str):
            if name_or_tid not in self._map:
                self.search(name_or_tid)
            if name_or_tid not in self._map:
                raise ValueError(f"Couldn't find tag with name {name_or_tid!r}")
            name_or_tid = self._map[name_or_tid]["id"]
        self.client.delete(self.endpoint, name_or_tid)

    def rename(self, name_or_tid: Union[str, int], new_name: str):
        if isinstance(name_or_tid, str):
            if name_or_tid not in self._map:
                self.search(name_or_tid)
            if name_or_tid not in self._map:
                raise ValueError(f"Couldn't find tag with name {name_or_tid!r}")
            name_or_tid = self._map[name_or_tid]["id"]
        self.client.put(self.endpoint, name_or_tid, json={"name": new_name})

    def add_to_ticket(self, tid: int, *names: str):
        for name in names:
            params = {"item": name, "object": "Ticket", "o_id": tid}
            self.client.post("tags/add", json=params)

    def remove_from_ticket(self, tid: int, *names: str):
        for name in names:
            params = {"item": name, "object": "Ticket", "o_id": tid}
            self.client.delete("tags/remove", json=params)

    def by_ticket(self, tid: int) -> List[str]:
        items: "StringKeyDict" = self.client.get(
            "tags", params={"object": "Ticket", "o_id": tid}
        )
        return items.get("tags", [])
