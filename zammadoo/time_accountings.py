#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from functools import cached_property
from typing import TYPE_CHECKING, Optional

from .resource import MutableResource, NamedResource, UserProperty
from .resources import CreatableT, IterableT

if TYPE_CHECKING:
    from .articles import Article
    from .client import Client
    from .tickets import Ticket
    from .utils import JsonDict


class TimeAccountingType(NamedResource):
    pass


class TimeAccountingTypes(
    IterableT[TimeAccountingType], CreatableT[TimeAccountingType]
):
    """TimeAccountingTypess(...)"""

    _RESOURCE_TYPE = TimeAccountingType

    def __init__(self, client: "Client"):
        super().__init__(client, "time_accounting/types")

    def cached_info(self, url: str, refresh=True, expand=False) -> "JsonDict":
        cache = self.cache
        if url not in cache or refresh:
            for _ in self:
                pass

        return cache[url]

    def create(
        self, name: str, *, note: Optional[str] = None, active: bool = True
    ) -> TimeAccountingType:
        """
        Create a new time accounting type.

        :param name: the type name
        :param note: optional note
        :param active: active flag
        :return: the newly created time accountings type
        :rtype: :class:`TimeAccountingType`
        """
        return self._create({"name": name, "note": note, "active": active})

    def delete(self, rid: int) -> None:
        """
        Since time_accounting types cannot be deletet via REST API, this method is not implemented

        :raises: :exc:`NotImplementedError`
        :meta private:
        """
        raise NotImplementedError(
            "time_accounting types cannot be deletet via REST API"
        )


class TimeAccounting(MutableResource):
    """TimeAccounting(...)"""

    EXPANDED_ATTRIBUTES = ("type",)

    id: int  #:
    parent: "TimeAccountings"
    ticket_id: int  #:
    ticket_article_id: Optional[int]  #:
    time_unit: str  #:
    updated_by = UserProperty("created_by")

    @property
    def ticket(self) -> "Ticket":
        return self.parent.client.tickets(self.ticket_id)

    @property
    def ticket_article(self) -> Optional["Article"]:
        aid = self.ticket_article_id
        return None if aid is None else self.parent.client.ticket_articles(aid)

    @property
    def type(self) -> Optional[TimeAccountingType]:
        type_id: int = self["type_id"]
        return None if type_id is None else self.parent.types(type_id)


class TimeAccountings(IterableT[TimeAccounting], CreatableT[TimeAccounting]):
    """TimeAccountings(...)"""

    _RESOURCE_TYPE = TimeAccounting

    def __init__(self, client: "Client"):
        super().__init__(client, "time_accountings")

    def create(
        self,
        ticket_id: int,
        **kwargs,
    ) -> TimeAccounting:
        return self._create(json={"ticket_id": ticket_id, **kwargs})

    @cached_property
    def types(self) -> TimeAccountingTypes:
        """Manages the ``/time_accounting/types`` endpoint."""
        return TimeAccountingTypes(self.client)
