#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple, Union

from .articles import Article
from .client import Client
from .organizations import Organization
from .resource import Resource, UpdatableResource
from .resources import IterableT, SearchableT
from .users import User
from .utils import JsonContainer, JsonDict

LINK_TYPES: Tuple[str, ...]
Group = Resource
Priority = Resource

class State(UpdatableResource):
    active: bool
    name: str
    next_state: "State"
    note: Optional[str]

class States(IterableT[State]):
    RESOURCE_TYPE = State

class Ticket(UpdatableResource):
    articles: List[Article]
    created_at: datetime
    created_by: User
    customer: User
    group: User
    note: str
    number: str
    organization: Optional[Organization]
    owner: User
    priority: Priority
    state: State
    title: str
    updated_by: User

    _resources: "Tickets"
    def tags(self) -> List[str]: ...
    def add_tags(self, *names: str) -> None: ...
    def remove_tags(self, *names: str) -> None: ...
    def links(self) -> Dict[str, List["Ticket"]]: ...
    def link_with(self, target_id: int, link_type: str = ...) -> None: ...
    def unlink_from(self, target_id: int, link_type: str = ...) -> None: ...
    def merge_with(self, target_id: int) -> bool: ...

class Tickets(SearchableT[Ticket]):
    RESOURCE_TYPE = Ticket

    def _iter_items(self, items: JsonContainer) -> Iterable[Ticket]: ...
    def create(
        self,
        title: str,
        group: Union[str, int],
        customer: Union[str, int],
        body: Optional[str] = ...,
        **kwargs,
    ) -> Ticket: ...

def cache_assets(client: Client, assets: Dict[str, Dict[str, JsonDict]]) -> None: ...
