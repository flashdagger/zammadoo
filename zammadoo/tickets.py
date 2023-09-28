#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import Iterable, cast

from .organizations import OrganizationProperty
from .resource import Resource, ResourceListProperty, ResourceProperty, datetime
from .resources import SearchableT
from .ticket_states import TicketStateProperty
from .users import UserProperty
from .utils import JsonContainer

Article = Resource
Group = Resource
Priority = Resource


class Ticket(Resource):
    articles = ResourceListProperty[Article]("ticket_articles")
    created_at: datetime
    created_by = UserProperty()
    customer = UserProperty()
    group = ResourceProperty()
    note: str
    number: str
    organization = OrganizationProperty()
    owner = UserProperty()
    priority = cast(Priority, ResourceProperty("ticket_priorities"))
    state = TicketStateProperty()
    title: str
    updated_by = UserProperty()

    def tags(self):
        return self._resources.client.tags.by_ticket(self.id)

    def add_tag(self, name: str):
        return self._resources.client.tags.add_to_ticket(name, self.id)

    def remove_tag(self, name: str):
        return self._resources.client.tags.remove_from_ticket(name, self.id)


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
