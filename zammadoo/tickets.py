#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import TYPE_CHECKING, List, Optional

from .resource import MutableResource, NamedResource, resource_property
from .resources import Creatable, IterableT, SearchableT
from .users import user_property
from .utils import LINK_TYPES

if TYPE_CHECKING:
    from .articles import Article
    from .groups import Group
    from .organizations import Organization
    from .users import User


class Priority(NamedResource):
    pass


class Priorities(IterableT[Priority], Creatable):
    RESOURCE_TYPE = Priority

    create = Creatable.create_with_name

    def __init__(self, client):
        super().__init__(client, "ticket_priorities")


class State(MutableResource):
    @resource_property("ticket_states")
    def next_state(self) -> "State":
        ...


class States(IterableT[State], Creatable):
    RESOURCE_TYPE = State

    def __init__(self, client):
        super().__init__(client, "ticket_states")

    def create(self, name, state_type_id, **kwargs):
        return super()._create({"name": name, "state_type_id": state_type_id, **kwargs})


class Ticket(MutableResource):
    article_count: Optional[int]
    note: str
    number: str
    title: str

    @user_property
    def customer(self) -> "User":
        ...

    @resource_property
    def group(self) -> "Group":
        ...

    @resource_property
    def organization(self) -> Optional["Organization"]:
        ...

    @user_property
    def owner(self) -> "User":
        """
        .. note::
           unassigned tickets will be represented by User(id=1)
        """

    @resource_property("ticket_priorities")
    def priority(self) -> Priority:
        ...

    @resource_property("ticket_states")
    def state(self) -> State:
        ...

    @property
    def articles(self) -> List["Article"]:
        """
        all articles related to the ticket as sent by ``/ticket_articles/by_ticket/{ticket id}``
        """
        articles = self.parent.client.ticket_articles

        try:
            rids = self["article_ids"]
        except KeyError:
            return articles.by_ticket(self._id)

        return [articles(rid) for rid in rids]

    def tags(self):
        """
        all tags that are related to the ticket as sent by ``/tags?object=Ticket&o_id={ticket id}``

        :rtype: :class:`List[str]`
        """
        return self.parent.client.tags.by_ticket(self.id)

    def add_tags(self, *names):
        """
        link given tags with ticket, if the tag is already linked with the ticket
        it will be ignored

        :param names: tag names
        :type names: :class:`str`
        """
        return self.parent.client.tags.add_to_ticket(self.id, *names)

    def remove_tags(self, *names):
        """
        remove given tags from ticket, if the tag is not linked with the ticket
        it will be ignored

        :param names: tag names
        :type names: :class:`str`
        """
        return self.parent.client.tags.remove_from_ticket(self.id, *names)

    def links(self):
        """
        returns all linked tickets grouped by link type

        :returns: ``{"normal": [Ticket, ...], "parent": [...], "child": [...]}``
        """
        parent = self.parent
        client = parent.client
        params = {"link_object": "Ticket", "link_object_value": self.id}
        link_map = dict((key, []) for key in LINK_TYPES)

        items = client.get("links", params=params)
        cache_assets(client, items.get("assets", {}))
        for item in items["links"]:
            assert item["link_object"] == "Ticket"
            link_type = item["link_type"]
            link_map.setdefault(link_type, []).append(parent(item["link_object_value"]))

        return link_map

    def link_with(self, target_id, link_type="normal"):
        """
        link the ticket with another one, if the link already
        exists it will be ignored

        :param target_id: the id of the related ticket
        :type target_id: :class:`int`
        :param link_type: specifies the relationship type
        :type link_type: ``"normal"``, ``"parent"``, ``"child"``
        """
        switch_map = {"parent": "child", "child": "parent"}
        params = {
            "link_type": switch_map.get(link_type, link_type),
            "link_object_target": "Ticket",
            "link_object_target_value": target_id,
            "link_object_source": "Ticket",
            "link_object_source_number": self["number"],
        }
        self.parent.client.post("links/add", json=params)

    def unlink_from(self, target_id, link_type="any"):
        """
        remove link with another, if the link does not exist it will be ignored

        :param target_id: the id of the related ticket
        :type target_id: :class:`int`
        :param link_type: specifies the relationship type, if omitted the ticket_id
                        will be looked up for every link_type
        :type link_type: ``"normal"``, ``"parent"``, ``"child"``
        """
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
        self.parent.client.delete("links/remove", json=params)

    def merge_with(self, target_id):
        """
        merges the ticket with another one

        :param target_id: the id of the ticket to be merged with
        :type target_id: :class:`int`
        :return: the merged ticket objects
        :rtype: :class:`Ticket`
        """
        parent = self.parent
        info = parent.client.put("ticket_merge", target_id, self["number"])
        assert info["result"] == "success", f"merge failed with {info['result']}"
        merged_info = info["target_ticket"]
        return parent(merged_info["id"], info=merged_info)

    def create_article(self, body, typ="note", internal=True, **kwargs):
        """
        Create a new article for the ticket.

        :param body: article body text
        :type body: :class:`str`
        :param typ: article type
        :type typ: :class:`str`
        :param internal: article visibility
        :type internal: :class:`bool`
        :param kwargs: additional article properties
        :return: the newly created article
        :rtype: :class:`.articles.Article`
        """
        return self.parent.client.ticket_articles.create(
            self._id, body=body, type=typ, internal=internal, **kwargs
        )


class Tickets(SearchableT[Ticket], Creatable):
    RESOURCE_TYPE = Ticket
    DEFAULT_CACHE_SIZE = 100

    def __init__(self, client):
        super().__init__(client, "tickets")

    def _iter_items(self, items):
        if isinstance(items, list):
            yield from super()._iter_items(items)
            return

        assert isinstance(items, dict)
        cache_assets(self.client, items.get("assets", {}))

        for rid in items.get("tickets", ()):
            yield self.RESOURCE_TYPE(self, rid)

    def create(self, title, *, group, customer, body=None, **kwargs):
        """
        Create a new ticket.

        :param title: ticket title
        :type title: :class:`str`
        :param group: group name or id
        :type group: :class:`str` | :class:`int`
        :param customer: customer name or id
        :type customer: :class:`str` | :class:`int`
        :param body: the text body of the first ticket articke
        :type body: :class:`str` | :class:`None`
        :param kwargs: additional ticket properties
        :returns: An instance of the created ticket.
        :rtype: :class:`Ticket`
        """
        group_key = "group_id" if isinstance(group, int) else "group"
        customer_key = "customer_id" if isinstance(customer, int) else "customer"
        article = kwargs.pop("article", {})
        if body is not None:
            article["body"] = body

        info = {
            "title": title,
            group_key: group,
            customer_key: customer,
            "article": article,
            **kwargs,
        }

        return super()._create(info)


def cache_assets(client, assets):
    for key, asset in assets.items():
        resources = getattr(client, f"{key.lower()}s")
        for rid_s, info in asset.items():
            url = resources.url(rid_s)
            resources.cache[url] = info
