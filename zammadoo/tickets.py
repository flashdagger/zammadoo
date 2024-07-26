#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Literal,
    Optional,
    TypedDict,
    Union,
    get_args,
)

from .resource import MutableResource, NamedResource, UserProperty
from .resources import CreatableT, IterableT, SearchableT
from .time_accountings import TimeAccounting, TimeAccountingType
from .utils import OptionalDateTime

if TYPE_CHECKING:
    from typing_extensions import Self

    from .articles import Article, OptionalFiles
    from .client import Client
    from .groups import Group
    from .organizations import Organization
    from .resource import Resource, TypedResourceDict
    from .resources import ResourcesT
    from .utils import JsonDict, StringKeyMapping


LinkType = Literal["normal", "parent", "child"]
LINK_TYPES = get_args(LinkType)


class _TypedJson(TypedDict):
    id: int
    assets: Dict[str, Dict[str, "JsonDict"]]
    history: List["StringKeyMapping"]
    links: List["StringKeyMapping"]


class Priority(NamedResource):
    """Priority(...)"""

    EXPANDED_ATTRIBUTES = ("created_by", "updated_by")

    ui_color: Optional[str]  #:
    ui_icon: Optional[str]  #:


class Priorities(IterableT[Priority], CreatableT[Priority]):
    """Priorities(...)"""

    _RESOURCE_TYPE = Priority

    def create(self, name: str, **kwargs) -> Priority:
        """
        Create a new priority.

        :param name: priority identifier name
        :param kwargs: additional priority properties
        :return: the newly created object
        :rtype: :class:`Priority`
        """
        return self._create({"name": name, **kwargs})

    def __init__(self, client: "Client"):
        super().__init__(client, "ticket_priorities")


class State(NamedResource):
    """State(...)"""

    EXPANDED_ATTRIBUTES = ("created_by", "state_type", "updated_by")

    parent: "States"

    default_create: bool  #:
    default_follow_up: bool  #:
    ignore_escalation: bool  #:

    @property
    def next_state(self) -> Optional["State"]:
        sid: Optional[int] = self["next_state_id"]
        return None if sid is None else self.parent(sid)

    @property
    def state_type(self) -> "State":
        sid: int = self["state_type_id"]
        return self.parent(sid)


class States(IterableT[State], CreatableT[State]):
    """States(...)"""

    _RESOURCE_TYPE = State

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


# pylint: disable=too-many-public-methods
class Ticket(MutableResource):
    """Ticket(...)"""

    EXPANDED_ATTRIBUTES = (
        "article_ids",
        "create_article_sender",
        "create_article_type",
        "created_by",
        "customer",
        "group",
        "organization",
        "owner",
        "priority",
        "state",
        "ticket_time_accounting",
        "ticket_time_accounting_ids",
        "updated_by",
    )

    article_count: Optional[int]  #:
    create_article_sender: str  #:
    create_article_type: str  #:
    note: Optional[str]  #:
    number: str  #:
    parent: "Tickets"
    time_unit: Optional[str]  #:
    title: str  #:

    close_at = OptionalDateTime()
    close_escalation_at = OptionalDateTime()
    customer = UserProperty()
    escalation_at = OptionalDateTime()
    first_response_at = OptionalDateTime()
    first_response_escalation_at = OptionalDateTime()
    last_contact_agent_at = OptionalDateTime()
    last_contact_at = OptionalDateTime()
    last_contact_customer_at = OptionalDateTime()
    last_owner_update_at = OptionalDateTime()
    #:
    #:  .. note::
    #:     unassigned tickets will be represented by User with id=1
    #:
    owner = UserProperty()
    update_escalation_at = OptionalDateTime()

    @property
    def group(self) -> "Group":
        gid: int = self["group_id"]
        return self.parent.client.groups(gid)

    @property
    def organization(self) -> Optional["Organization"]:
        oid: Optional[int] = self["organization_id"]
        return None if oid is None else self.parent.client.organizations(oid)

    @property
    def priority(self) -> Priority:
        pid: int = self["priority_id"]
        return self.parent.client.ticket_priorities(pid)

    @property
    def state(self) -> State:
        sid: int = self["state_id"]
        return self.parent.client.ticket_states(sid)

    @property
    def articles(self) -> List["Article"]:
        """
        all articles related to the ticket as sent by ``/ticket_articles/by_ticket/{ticket id}``
        """
        articles = self.parent.client.ticket_articles
        article_ids: List[int] = self["article_ids"]
        return [articles(aid) for aid in sorted(article_ids)]

    def time_accountings(self) -> List[TimeAccounting]:
        """
        :return: all time accounting objects for the ticket.
        """
        parent = self.parent
        client = parent.client
        time_accountings = client.time_accountings
        time_accountings_list: List["TypedResourceDict"] = client.get(
            parent.endpoint, self.id, "time_accountings", _erase_return_type=True
        )
        return [
            time_accountings(info["id"], info=info) for info in time_accountings_list
        ]

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

        To loop over all linked tickets at once use `itertools.chain()`:

        ::

            for linked_ticked in itertools.chain(*ticket.links().values()):
                print(linked_ticket)

        :return: ``{"normal": [Ticket, ...], "parent": [...], "child": [...]}``
        """

        parent = self.parent
        client = parent.client
        items: _TypedJson = client.get(
            "links",
            params={"link_object": "Ticket", "link_object_value": self.id},
            _erase_return_type=True,
        )
        cache_assets(client, items["assets"])

        link_map: Dict[str, List["Ticket"]] = {}
        for item in items["links"]:
            assert item["link_object"] == "Ticket"
            link_map.setdefault(item["link_type"], []).append(
                parent(item["link_object_value"])
            )
        for link_type in LINK_TYPES:
            if link_type not in link_map:
                link_map[link_type] = []

        return link_map

    def link_with(self, target: Union[int, "Ticket"], link_type: LinkType = "normal"):
        """
        link the ticket with another one, if the link already
        exists it will be ignored

        :param target: the target ticket or its id
        :type target: :class:`Ticket` | int
        :param link_type: specifies the relationship type
        """
        switch_map = {"parent": "child", "child": "parent"}
        params = {
            "link_type": switch_map.get(link_type, link_type),
            "link_object_target": "Ticket",
            "link_object_target_value": (
                target if isinstance(target, int) else target.id
            ),
            "link_object_source": "Ticket",
            "link_object_source_number": self["number"],
        }
        self.parent.client.post("links/add", json=params)

    def unlink_from(
        self, target: Union[int, "Ticket"], link_type: Optional[LinkType] = None
    ) -> None:
        """
        remove the link to another ticket, if the link does not exist it will be ignored

        :param target: the target ticket or its id
        :type target: :class:`Ticket` | int
        :param link_type: specifies the relationship type, if omitted the ticket_id
                          will be looked up for every link_type
        """
        for _link_type, tickets in self.links().items():
            if link_type not in {None, _link_type}:
                continue

            target_id = target if isinstance(target, int) else target.id
            if target_id not in {ticket.id for ticket in tickets}:
                continue

            params = {
                "link_type": _link_type,
                "link_object_target": "Ticket",
                "link_object_target_value": self.id,
                "link_object_source": "Ticket",
                "link_object_source_value": target_id,
            }
            self.parent.client.delete("links/remove", json=params)

    def merge_into(self, target: Union[int, "Ticket"]) -> "Ticket":
        """
        merges the ticket into another

        .. note::
            this method uses an undocumented API endpoint

        :param target: the target ticket or its id
        :type target: :class:`Ticket` | int
        :return: the merged ticket object
        :rtype: :class:`Ticket`
        """
        parent = self.parent
        if isinstance(target, int):
            target = parent(target)

        info = parent.client.put("ticket_merge", self.id, target["number"])
        assert isinstance(info, dict)
        assert info["result"] == "success", f"merge failed with {info['result']}"

        merged_info = info["target_ticket"]
        assert isinstance(merged_info, dict)
        assert isinstance(merged_info["id"], int)

        return parent(merged_info["id"], info=merged_info)

    def create_article(
        self,
        body: str,
        *,
        typ: str = "note",
        internal: bool = True,
        files: "OptionalFiles" = None,
        **kwargs,
    ) -> "Article":
        """
        Create a new article for the ticket.

        :param body: article body text
        :param typ: article type
        :param internal: article visibility
        :param files: attachment files
        :param kwargs: additional article properties
        :return: the newly created article
        """
        return self.parent.client.ticket_articles.create(
            self.id,
            body=body,
            files=files,
            type=typ,
            internal=internal,
            **kwargs,
        )

    def create_time_accounting(
        self, time_unit: Union[str, float], **kwargs
    ) -> "TimeAccounting":
        """
        Add accounted time to ticket.

        :param time_unit: accounted time units
        :param kwargs: type(`str` | :class:`TimeAccountingType`)
        :rtype: :class:`TimeAccounting`
        """
        kwargs["time_unit"] = str(time_unit)
        ta_type = kwargs.get("type")
        if isinstance(ta_type, TimeAccountingType):
            kwargs.pop("type")
            kwargs["type_id"] = ta_type.id

        return self.parent.client.time_accountings.create(self.id, **kwargs)

    def update(self, **kwargs) -> "Self":
        """
        Update the ticket properties.

        :param kwargs: additional values to be updated
        :return: a new instance of the updated ticket
        :rtype: :class:`Ticket`
        """
        body = kwargs.pop("body", None)
        if body:
            article = kwargs.setdefault("article", {})
            article.setdefault("body", body)
            article.setdefault("internal", kwargs.pop("internal", True))

        return super().update(**kwargs)

    def history(self) -> List["StringKeyMapping"]:
        """
        .. note::
            this method uses an undocumented API endpoint

        :return: the ticket's history
        """
        info: _TypedJson = self.parent.client.get(
            "ticket_history", self.id, _erase_return_type=True
        )
        return info["history"]

    @property
    def weburl(self) -> str:
        """URL of the ticket in the webclient"""
        return f"{self.parent.client.weburl}/#ticket/zoom/{self.id}"


class Tickets(SearchableT[Ticket], CreatableT[Ticket]):
    """Tickets(...)"""

    _RESOURCE_TYPE = Ticket
    DEFAULT_CACHE_SIZE = 100

    def __init__(self, client: "Client"):
        super().__init__(client, "tickets")

    def _iter_items(self, items: Union["StringKeyMapping", List["JsonDict"]]):
        if isinstance(items, list):
            yield from super()._iter_items(items)
            return

        cache_assets(self.client, items.get("assets", {}))

        for rid in items.get("tickets", ()):
            yield self._RESOURCE_TYPE(self, rid)

    def create(
        self,
        title: str,
        group: Union[str, int],
        customer: Union[str, int],
        article: Union[str, "StringKeyMapping"],
        **kwargs,
    ) -> Ticket:
        """
        Create a new ticket.

        :param title: ticket title
        :param group: group name or id
        :param customer: customer email or id, you can also use `guess:<email>`
        :param article: the text body of the first ticket article or the article mapping
        :param kwargs: additional ticket properties
        :return: An instance of the created ticket.
        """
        group_key = "group_id" if isinstance(group, int) else "group"
        customer_key = (
            "customer_id"
            if isinstance(customer, int) or customer.startswith("guess:")
            else "customer"
        )
        if isinstance(article, str):
            article = {"body": article}

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
        resources: "ResourcesT[Resource]" = getattr(client, f"{key.lower()}s")
        for rid_s, info in asset.items():
            url = f"{resources.url}/{rid_s}"
            resources.cache[url] = info
