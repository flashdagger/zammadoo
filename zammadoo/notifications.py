#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, Iterator, List, Optional

from .resource import MutableResource, UserProperty
from .resources import IterableT

if TYPE_CHECKING:
    from .client import Client
    from .utils import JsonDict


class Notification(MutableResource):
    """Notification(...)"""

    EXPANDED_ATTRIBUTES = ("object", "type", "user")

    parent: "Notifications"
    object: str
    seen: bool
    type: str
    user = UserProperty()

    # always use expand=True
    def reload(self, expand=True) -> None:
        return super().reload(expand=True)

    # always use expand=True
    def _assert_attribute(self, name: Optional[str] = None) -> None:
        return super()._assert_attribute(name="object")


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
