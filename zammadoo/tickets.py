#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import UpdatableResource, resource_property
from .resources import IterableT, SearchableT
from .users import user_property

LINK_TYPES = ("normal", "parent", "child")


class State(UpdatableResource):
    @resource_property("ticket_states")
    def next_state(self):
        ...


class States(IterableT[State]):
    RESOURCE_TYPE = State


class Ticket(UpdatableResource):
    @user_property
    def customer(self):
        ...

    @resource_property
    def group(self):
        ...

    @resource_property
    def organization(self):
        ...

    @user_property
    def owner(self):
        ...

    @resource_property("ticket_priorities")
    def priority(self):
        ...

    @resource_property("ticket_states")
    def state(self):
        ...

    @property
    def articles(self):
        articles = self._resources.client.ticket_articles

        try:
            rids = self["article_ids"]
        except KeyError:
            return articles.by_ticket(self._id)

        return [articles(rid) for rid in rids]

    def tags(self):
        return self._resources.client.tags.by_ticket(self.id)

    def add_tags(self, *names):
        return self._resources.client.tags.add_to_ticket(self.id, *names)

    def remove_tags(self, *names):
        return self._resources.client.tags.remove_from_ticket(self.id, *names)

    def links(self):
        resources = self._resources
        params = {"link_object": "Ticket", "link_object_value": self.id}
        link_map = dict((key, []) for key in LINK_TYPES)

        items = resources.client.get("links", params=params)
        cache_assets(resources.client, items.get("assets", {}))
        for item in items["links"]:
            assert item["link_object"] == "Ticket"
            link_type = item["link_type"]
            link_map.setdefault(link_type, []).append(
                resources(item["link_object_value"])
            )

        return link_map

    def link_with(self, target_id, link_type="normal"):
        assert (
            link_type in LINK_TYPES
        ), f"parameter link_type must be one of {LINK_TYPES}"
        resources = self._resources
        params = {
            "link_type": link_type,
            "link_object_target": "Ticket",
            "link_object_target_value": target_id,
            "link_object_source": "Ticket",
            "link_object_source_number": self["number"],
        }
        resources.client.post("links/add", json=params)

    def unlink_from(self, target_id, link_type="any"):
        resources = self._resources
        if link_type not in LINK_TYPES:
            link_type = "normal"
            for _link_type, tickets in self.links().items():
                if target_id in {ticket.id for ticket in tickets}:
                    link_type = _link_type

        params = {
            "link_type": link_type,
            "link_object_target": "Ticket",
            "link_object_target_value": self._id,
            "link_object_source": "Ticket",
            "link_object_source_value": target_id,
        }
        resources.client.delete("links/remove", json=params)

    def merge_with(self, target_id):
        resources = self._resources
        info = resources.client.put("ticket_merge", target_id, self["number"])
        if info.get("result") == "success":
            ticket_info = info["target_ticket"]
            assert isinstance(ticket_info, dict)
            assert ticket_info["id"] == self._id
            resources.cache[self._url] = ticket_info
            self._info.clear()
            return True

        return False


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


def cache_assets(client, assets):
    for key, asset in assets.items():
        resources = getattr(client, f"{key.lower()}s")
        for rid_s, info in asset.items():
            url = resources.url(rid_s)
            resources.cache[url] = info
