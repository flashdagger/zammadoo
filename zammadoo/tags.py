#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from types import MappingProxyType
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, TypedDict

if TYPE_CHECKING:
    from .client import Client
    from .utils import StringKeyMapping


class TypedTag(TypedDict):
    id: int
    name: str
    count: Optional[int]


class _TypedJson(TypedTag, total=False):
    value: str
    tags: List[str]


class Tags:
    """Tags(...)
    This class manages the ``/tags``, ``/tag_list`` and ``/tag_search`` endpoint.
    """

    def __init__(self, client: "Client"):
        self.client = client
        self.cache: Dict[str, TypedTag] = {}
        self.endpoint = "tag_list"
        self._unintialized = True

    def __repr__(self):
        url = f"{self.client.url}/{self.endpoint}"
        return f"<{self.__class__.__qualname__} {url!r}>"

    def __iter__(self) -> Iterator["StringKeyMapping"]:
        if self._unintialized:
            self.reload()
        return (MappingProxyType(value) for value in self.cache.values())

    def __getitem__(self, item: str) -> "StringKeyMapping":
        if self._unintialized:
            self.reload()
        return MappingProxyType(self.cache[item])

    def __contains__(self, item: str) -> bool:
        if self._unintialized:
            self.reload()
        return item in self.cache

    def reload(self) -> None:
        """reloads the tag cache"""
        cache = self.cache
        items: List[TypedTag] = self.client.get(self.endpoint, _erase_return_type=True)

        cache.clear()
        cache.update((info["name"], info) for info in items)
        self._unintialized = False

    def search(self, term: str) -> List[str]:
        """
        find matching tags

        :param term: search term
        :return: search results
        """
        items: List["_TypedJson"] = self.client.get(
            "tag_search", params={"term": term}, _erase_return_type=True
        )
        return list(info["value"] for info in items)

    def create(self, name: str) -> None:
        """
        creates a new tag (admin only), if name already exists, it is ignored
        """
        cache = self.cache
        self.client.post(self.endpoint, json={"name": name})
        if name not in cache:
            self._unintialized = True

    def delete(self, name: str) -> None:
        """
        deletes an existing tag (admin only)

        :param name: tag name
        :raises: :class:`KeyError` if not found
        """
        cache = self.cache
        if name not in cache:
            self.reload()
        self.client.delete(self.endpoint, cache.pop(name)["id"])

    def rename(self, name: str, new_name: str) -> None:
        """
        rename an existing tag (admin only)

        if the new name already exists, the current name will be deleted

        :param name: the current name
        :param new_name: new name
        :raises: :class:`KeyError` if not found
        """
        cache = self.cache
        if name not in cache:
            self.reload()

        self.client.put(self.endpoint, cache[name]["id"], json={"name": new_name})
        tag = cache[new_name] = cache.pop(name)
        tag["name"] = new_name

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
        all tags that are associated with a ticket

        :param tid: the ticket id
        :return: ticket tags
        """
        items: "_TypedJson" = self.client.get(
            "tags", params={"object": "Ticket", "o_id": tid}, _erase_return_type=True
        )
        return items["tags"]
