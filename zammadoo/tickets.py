#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import Iterable, Optional, cast

from .organizations import Organization
from .resource import Resource, ResourceListGetter, ResourceProperty, datetime
from .resources import SearchableT
from .ticket_states import TicketStateProperty
from .users import User, UserProperty
from .utils import JsonContainer

Article = Resource
Group = Resource
Priority = Resource


class Ticket(Resource):
    articles = ResourceListGetter[Article]("ticket_articles")
    created_at: datetime
    created_by = UserProperty()
    customer = UserProperty()
    group = cast(Group, ResourceProperty())
    note: str
    number: str
    organization = cast(Organization, ResourceProperty())
    owner = UserProperty()
    priority = cast(Priority, ResourceProperty("ticket_priorities"))
    state = TicketStateProperty()
    title: str
    updated_by = cast(Optional[User], UserProperty())


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
