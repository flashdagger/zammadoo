#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, Dict, List, Optional, Union, cast

from .resource import MutableResource, NamedResource
from .resources import Creatable, IterableT, SearchableT
from .utils import LINK_TYPE, LINK_TYPES

if TYPE_CHECKING:
    from .articles import Article
    from .client import Client
    from .groups import Group
    from .organizations import Organization
    from .types import JsonDict
    from .users import User


class Priority(NamedResource):
    pass


class Priorities(IterableT[Priority], Creatable[Priority]):
    RESOURCE_TYPE = Priority

    create = Creatable.create_with_name

    def __init__(self, client: "Client"):
        super().__init__(client, "ticket_priorities")


class State(MutableResource):
    @property
    def next_state(self) -> "State":
        sid = self["next_state_id"]
        return self.parent.client.ticket_states(sid)


class States(IterableT[State], Creatable[State]):
    RESOURCE_TYPE = State

    def __init__(self, client: "Client"):
        super().__init__(client, "ticket_states")

    def create(self, name: str, state_type_id: int, **kwargs) -> "State":
        """
        Create a new state.

        :param name: state name
        :param state_type_id: the states type id
        :param kwargs: additional resource properties
        :return: the newly created object
        :rtype: :class:`State`
        """
        return super()._create({"name": name, "state_type_id": state_type_id, **kwargs})


class Ticket(MutableResource):
    article_count: Optional[int]  #:
    note: str  #:
    number: str  #:
    title: str  #:

    @property
    def customer(self) -> "User":
        uid = self["customer_id"]
        return self.parent.client.users(uid)

    @property
    def group(self) -> "Group":
        gid = self["group_id"]
        return self.parent.client.groups(gid)

    @property
    def organization(self) -> Optional["Organization"]:
        oid = self["organization_id"]
        return oid and self.parent.client.organizations(oid)

    @property
    def owner(self) -> "User":
        """
        .. note::
           unassigned tickets will be represented by User(id=1)
        """
        uid = self["owner_id"]
        return self.parent.client.users(uid)

    @property
    def priority(self) -> Priority:
        pid = self["priority_id"]
        return self.parent.client.ticket_priorities(pid)

    @property
    def state(self) -> State:
        sid = self["state_id"]
        return self.parent.client.ticket_states(sid)

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

    def tags(self) -> List[str]:
        """
        :return: | all tags that are related to the ticket as sent by
                 | ``/tags?object=Ticket&o_id={ticket id}``
        """
        return self.parent.client.tags.by_ticket(self.id)

    def add_tags(self, *names: str) -> None:
        """
        link given tags with ticket, if the tag is already linked with the ticket
        it will be ignored

        :param names: tag names
        """
        return self.parent.client.tags.add_to_ticket(self.id, *names)

    def remove_tags(self, *names: str) -> None:
        """
        remove given tags from ticket, if the tag is not linked with the ticket
        it will be ignored

        :param names: tag names
        """
        return self.parent.client.tags.remove_from_ticket(self.id, *names)

    def links(self) -> Dict[str, List["Ticket"]]:
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

    def link_with(self, target_id: int, link_type: LINK_TYPE = "normal"):
        """
        link the ticket with another one, if the link already
        exists it will be ignored

        :param target_id: the id of the related ticket
        :param link_type: specifies the relationship type
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

    def unlink_from(
        self, target_id: int, link_type: Optional[LINK_TYPE] = None
    ) -> None:
        """
        remove link with another, if the link does not exist it will be ignored

        :param target_id: the id of the related ticket
        :param link_type: specifies the relationship type, if omitted the ticket_id
                          will be looked up for every link_type
        """
        for _link_type, tickets in self.links().items():
            if link_type not in {None, _link_type}:
                continue

            if target_id not in {ticket.id for ticket in tickets}:
                continue

            params = {
                "link_type": _link_type,
                "link_object_target": "Ticket",
                "link_object_target_value": self._id,
                "link_object_source": "Ticket",
                "link_object_source_value": target_id,
            }
            self.parent.client.delete("links/remove", json=params)

    def merge_with(self, target_id: int) -> "Ticket":
        """
        merges the ticket with another one

        :param target_id: the id of the ticket to be merged with
        :return: the merged ticket objects
        :rtype: :class:`Ticket`
        """
        parent = self.parent
        info = parent.client.put("ticket_merge", target_id, self["number"])
        assert info["result"] == "success", f"merge failed with {info['result']}"
        merged_info = info["target_ticket"]
        return cast("Ticket", parent(merged_info["id"], info=merged_info))

    def create_article(
        self, body: str, typ: str = "note", internal: bool = True, **kwargs
    ) -> "Article":
        """
        Create a new article for the ticket.

        :param body: article body text
        :param typ: article type
        :param internal: article visibility
        :param kwargs: additional article properties
        :return: the newly created article
        """
        return self.parent.client.ticket_articles.create(
            self._id, body=body, type=typ, internal=internal, **kwargs
        )


class Tickets(SearchableT[Ticket], Creatable[Ticket]):
    RESOURCE_TYPE = Ticket
    DEFAULT_CACHE_SIZE = 100

    def __init__(self, client: "Client"):
        super().__init__(client, "tickets")

    def _iter_items(self, items):
        if isinstance(items, list):
            yield from super()._iter_items(items)
            return

        assert isinstance(items, dict)
        cache_assets(self.client, items.get("assets", {}))

        for rid in items.get("tickets", ()):
            yield self.RESOURCE_TYPE(self, rid)

    def create(
        self,
        title: str,
        group: Union[str, int],
        customer: Union[str, int],
        body: Optional[str] = None,
        **kwargs,
    ) -> Ticket:
        """
        Create a new ticket.

        :param title: ticket title
        :param group: group name or id
        :param customer: customer name or id
        :param body: the text body of the first ticket articke
        :param kwargs: additional ticket properties
        :returns: An instance of the created ticket.
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


def cache_assets(client: "Client", assets: Dict[str, Dict[str, "JsonDict"]]) -> None:
    for key, asset in assets.items():
        resources = getattr(client, f"{key.lower()}s")
        for rid_s, info in asset.items():
            url = resources.url(rid_s)
            resources.cache[url] = info
