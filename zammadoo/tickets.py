#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import Iterable, Optional, cast

from .articles import ArticleListProperty
from .organizations import OrganizationProperty
from .resource import Resource, ResourceProperty, datetime
from .resources import IterableT, SearchableT
from .users import UserProperty
from .utils import JsonContainer

Group = Resource
Priority = Resource


class State(Resource):
    created_by = UserProperty()
    updated_by = UserProperty()


class States(IterableT[State]):
    RESOURCE_TYPE = State


class StateProperty(ResourceProperty[State]):
    def __init__(self, key=None):
        super().__init__(endpoint="ticket_states", key=key or "")


class Ticket(Resource):
    articles = ArticleListProperty()
    created_at: datetime
    created_by = UserProperty()
    customer = UserProperty()
    group = ResourceProperty()
    note: str
    number: str
    organization = OrganizationProperty()
    owner = UserProperty()
    priority = cast(Priority, ResourceProperty("ticket_priorities"))
    state = StateProperty()
    title: str
    updated_by = UserProperty()

    def tags(self):
        return self._resources.client.tags.by_ticket(self.id)

    def add_tags(self, *names: str):
        return self._resources.client.tags.add_to_ticket(self.id, *names)

    def remove_tags(self, *names: str):
        return self._resources.client.tags.remove_from_ticket(self.id, *names)


class Tickets(SearchableT[Ticket]):
    RESOURCE_TYPE = Ticket

    def _iter_items(self, items: JsonContainer) -> Iterable[Ticket]:
        if isinstance(items, list):
            yield from super()._iter_items(items)
            return

        assert isinstance(items, dict)
        for key, asset in items.get("assets", {}).items():
            resources = getattr(self.client, f"{key.lower()}s")
            for rid_s, info in asset.items():
                url = resources.url(rid_s)
                resources.cache[url] = info

        for rid in items.get("tickets", ()):
            yield self.RESOURCE_TYPE(self, rid)


class TicketProperty(ResourceProperty[Ticket]):
    def __init__(self, key: Optional[str] = None):
        super().__init__(endpoint="tickets", key=key or "")
