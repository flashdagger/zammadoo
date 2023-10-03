#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import Dict, Iterable, List, Literal, Optional, Tuple, Union

from .articles import Article
from .client import Client
from .organizations import Organization
from .resource import MutableResource, NamedResource
from .resources import Creatable, IterableT, SearchableT
from .users import User
from .utils import JsonContainer, JsonDict

LINK_TYPES: Tuple[str, ...]
LINK_TYPE = Literal["normal", "parent", "child"]

class Priority(NamedResource):
    default_create: bool
    ui_icon: str
    ui_color: str
    def update(self, **kwargs) -> "Priority": ...

class Priorities(IterableT[Priority], Creatable):
    RESOURCE_TYPE = Priority
    def create(self, name: str, **kwargs) -> Priority: ...

class State(MutableResource):
    active: bool
    name: str
    next_state: "State"
    note: Optional[str]
    def update(self, **kwargs) -> "State": ...

class States(IterableT[State]):
    RESOURCE_TYPE = State
    def create(self, name: str, **kwargs) -> State: ...

class Ticket(MutableResource):
    articles: List[Article]
    customer: User
    group: User
    note: str
    number: str
    organization: Optional[Organization]
    owner: User
    priority: Priority
    state: State
    title: str

    def tags(self) -> List[str]: ...
    def add_tags(self, *names: str) -> None: ...
    def remove_tags(self, *names: str) -> None: ...
    def links(self) -> Dict[str, List["Ticket"]]: ...
    def link_with(self, target_id: int, link_type: LINK_TYPE = ...) -> None: ...
    def unlink_from(self, target_id: int, link_type: LINK_TYPE = ...) -> None: ...
    def merge_with(self, target_id: int) -> "Ticket": ...
    def update(self, **kwargs) -> "Ticket": ...

class Tickets(SearchableT[Ticket], Creatable):
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
