#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional, Union

from .resource import MutableResource
from .resources import CreatableT, IterableT, _T_co
from .utils import FrozenInfo

if TYPE_CHECKING:
    from .articles import Article
    from .client import Client
    from .tickets import Ticket
    from .users import User
    from .utils import JsonDict


class TimeAccounting(MutableResource):
    """TimeAccounting(...)"""

    EXPANDED_ATTRIBUTES = ("type",)

    id: int  #:
    ticket_id: int  #:
    ticket_article_id: Optional[int]  #:
    created_at: datetime  #:
    created_by_id: int  #:
    updated_at: datetime  #:
    time_unit: str  #:
    url: str  #: the API endpoint URL

    @property
    def updated_by(self) -> "User":
        return self.created_by

    @property
    def ticket(self) -> "Ticket":
        return self.parent.client.tickets(self.ticket_id)

    @property
    def ticket_article(self) -> Optional["Article"]:
        aid = self.ticket_article_id
        return None if aid is None else self.parent.client.ticket_articles(aid)

    @property
    def type(self) -> Optional[str]:
        type_id: int = self["type_id"]
        parent: "TimeAccountings" = self.parent  # type: ignore[assignment]
        return None if type_id is None else parent.types[type_id].name

    def update(self: _T_co, **kwargs) -> _T_co:
        """
        Update the resource. Required permission: ``admin.time_accounting``.

        examples::

            time_accounting = client.time_accountings(1)

            # time_unit can be ``float`` or ``str``
            new_instance = time_accounting.update(time_unit=60.0)

            # change accounting type: ``str`` or type_id: ``int``
            new_instance = time_accounting.update(type="research")

            # change accounting type to default
            new_instance = time_accounting.update(type_id=None)


        :return: a new instance of the updated time accounting
        """
        assert (kwargs.keys() - {"time_unit", "type", "type_id", "article_id"}) == set()
        return super().update(**kwargs)


class TimeAccountingsType(FrozenInfo):
    id: int
    name: str
    note: str
    active: bool
    created_at: datetime
    updated_at: datetime


class TimeAccountings(IterableT[TimeAccounting], CreatableT[TimeAccounting]):
    """TimeAccountings(...)"""

    _RESOURCE_TYPE = TimeAccounting

    def __init__(self, client: "Client"):
        self._types: Optional[Dict[int, TimeAccountingsType]] = None
        super().__init__(client, "time_accountings")

    def create(
        self,
        time_unit: Union[str, float],
        ticket: Union["Ticket", int],
        type_: Union[None, int, str] = None,
    ) -> TimeAccounting:
        json: "JsonDict" = {
            "time_unit": time_unit,
            "ticket_id": ticket if isinstance(ticket, int) else ticket.id,
        }
        if type_:
            key = "type" if isinstance(type_, str) else "type_id"
            json[key] = type_

        return self._create(json=json)

    @property
    def types(self) -> Dict[int, TimeAccountingsType]:
        """returns a mapping of properties for each defined accounting type"""
        if self._types is None:
            self._types = {
                info["id"]: TimeAccountingsType(info)
                for info in self.client.get("time_accounting/types")
            }
        return self._types
