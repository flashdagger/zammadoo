#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .articles import ArticleListProperty
from .organizations import OrganizationProperty
from .resource import Resource, ResourceProperty
from .resources import IterableT, SearchableT
from .users import UserProperty


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
    created_by = UserProperty()
    customer = UserProperty()
    group = ResourceProperty()
    organization = OrganizationProperty()
    owner = UserProperty()
    priority = ResourceProperty("ticket_priorities")
    state = StateProperty()
    updated_by = UserProperty()

    def tags(self):
        return self._resources.client.tags.by_ticket(self.id)

    def add_tags(self, *names):
        return self._resources.client.tags.add_to_ticket(self.id, *names)

    def remove_tags(self, *names):
        return self._resources.client.tags.remove_from_ticket(self.id, *names)

    def relations(self):
        resources = self._resources
        params = {"link_object": "Ticket", "link_object_value": self.id}
        link_map = {"normal": [], "parent": [], "child": []}

        items = resources.client.get("links", params=params)
        cache_assets(resources.client, items.get("assets", {}))
        for item in items["links"]:
            assert item["link_object"] == "Ticket"
            link_type = item["link_type"]
            link_map.setdefault(link_type, []).append(
                resources(item["link_object_value"])
            )

        return link_map


class Tickets(SearchableT[Ticket]):
    RESOURCE_TYPE = Ticket
    CACHE_SIZE = 100

    def _iter_items(self, items):
        if isinstance(items, list):
            yield from super()._iter_items(items)
            return

        assert isinstance(items, dict)
        cache_assets(self.client, items.get("assets", {}))

        for rid in items.get("tickets", ()):
            yield self.RESOURCE_TYPE(self, rid)


class TicketProperty(ResourceProperty[Ticket]):
    def __init__(self, key=None):
        super().__init__(endpoint="tickets", key=key or "")


def cache_assets(client, assets):
    for key, asset in assets.items():
        resources = getattr(client, f"{key.lower()}s")
        for rid_s, info in asset.items():
            url = resources.url(rid_s)
            resources.cache[url] = info
