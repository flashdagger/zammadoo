#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Union

from .utils import info_cast

if TYPE_CHECKING:
    from .client import Client
    from .utils import StringKeyDict


class Tags:
    """Tags(...)
    This class manages the ``/tags``, ``/tag_list`` and ``/tag_search`` endpoint.
    """

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
        """
        :return: all existing tags (admin only)
        """
        self._reload()
        return list(self._map.keys())

    def search(self, term: str) -> List[str]:
        """
        find matching tags

        :param term: search term
        :return: search results
        """
        items = self.client.get("tag_search", params={"term": term})

        for info in items:
            name = info.pop("value")
            info.update((("name", name), ("count", None)))
            self._map.setdefault(name, info)

        return list(info["name"] for info in items)

    def create(self, name: str) -> None:
        """creates a new tag (admin only)"""
        self.client.post(self.endpoint, json={"name": name})

    def delete(self, name_or_tid: Union[str, int]) -> None:
        """
        deletes an existing tag (admin only)

        :param name_or_tid: the name or tag id, if not found it is ignored
        """
        if isinstance(name_or_tid, str):
            if name_or_tid not in self._map:
                self.search(name_or_tid)
            if name_or_tid not in self._map:
                raise ValueError(f"Couldn't find tag with name {name_or_tid!r}")
            name_or_tid = self._map[name_or_tid]["id"]
        self.client.delete(self.endpoint, name_or_tid)

    def rename(self, name_or_tid: Union[str, int], new_name: str) -> None:
        """rename an existing tag (admin only)

        :param name_or_tid: the name or tag id
        :param new_name: new name
        """
        if isinstance(name_or_tid, str):
            if name_or_tid not in self._map:
                self.search(name_or_tid)
            if name_or_tid not in self._map:
                raise ValueError(f"Couldn't find tag with name {name_or_tid!r}")
            name_or_tid = self._map[name_or_tid]["id"]
        self.client.put(self.endpoint, name_or_tid, json={"name": new_name})

    def add_to_ticket(self, tid: int, *names: str) -> None:
        """
        add one or more tags to the specified ticket, if the tag
        is already linked with the ticket it is ignored

        :param tid: the ticket id
        :param names: tag names
        """
        for name in names:
            params = {"item": name, "object": "Ticket", "o_id": tid}
            self.client.post("tags/add", json=params)

    def remove_from_ticket(self, tid: int, *names: str) -> None:
        """
        remove one or more tags from the specified ticket, if the tag
        is not linked with the ticket it is ignored

        :param tid: the ticket id
        :param names: tag names
        """
        for name in names:
            params = {"item": name, "object": "Ticket", "o_id": tid}
            self.client.delete("tags/remove", json=params)

    def by_ticket(self, tid: int) -> List[str]:
        """
        :param tid: the ticket id
        :return: all tags that are associated with a ticket
        """
        items: "StringKeyDict" = self.client.get(
            "tags", params={"object": "Ticket", "o_id": tid}
        )
        return info_cast(items).get("tags", [])
