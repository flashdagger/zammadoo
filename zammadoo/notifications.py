#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, Iterator, List

from .resource import MutableResource, UserProperty
from .resources import IterableT

if TYPE_CHECKING:
    from .client import Client
    from .utils import JsonDict


class Notification(MutableResource):
    """Notification(...)"""

    EXPANDED_ATTRIBUTES = ("*", "created_by", "object", "type", "updated_by", "user")

    object: str
    parent: "Notifications"
    seen: bool
    type: str
    user = UserProperty()


class Notifications(IterableT[Notification]):
    """Notifications(...)"""

    _RESOURCE_TYPE = Notification

    def __init__(self, client: "Client"):
        super().__init__(client, "online_notifications")

    def iter(self, *args, **params) -> Iterator[Notification]:
        items: List["JsonDict"] = self.client.get(
            self.endpoint, *args, params={"expand": True}, _erase_return_type=True
        )
        yield from self._iter_items(items)

    def mark_all_as_read(self) -> None:
        self.client.post(f"{self.endpoint}/mark_all_as_read")
        self.cache.clear()
