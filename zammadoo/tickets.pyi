#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

from .articles import Article
from .client import Client
from .organizations import Organization
from .resource import Resource, ResourceProperty
from .resources import IterableT, SearchableT
from .users import User
from .utils import JsonContainer, JsonDict

LINK_TYPES: Tuple[str, ...]
Group = Resource
Priority = Resource

class State(Resource):
    created_at: datetime
    created_by: User
    name: str
    note: Optional[str]
    updated_at: datetime
    updated_by: User

class States(IterableT[State]):
    RESOURCE_TYPE = State

class StateProperty(ResourceProperty[State]):
    def __init__(self, key: Optional[str] = ...) -> None: ...

class Ticket(Resource):
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
    def unlink_from(self, target: int) -> None: ...

class Tickets(SearchableT[Ticket]):
    RESOURCE_TYPE = Ticket

    def _iter_items(self, items: JsonContainer) -> Iterable[Ticket]: ...

class TicketProperty(ResourceProperty[Ticket]):
    def __init__(self, key: Optional[str] = ...): ...

def cache_assets(client: Client, assets: Dict[str, Dict[str, JsonDict]]) -> None: ...
