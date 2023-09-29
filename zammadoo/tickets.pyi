#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import List, Optional

from .articles import Article
from .organizations import Organization
from .resource import Resource, ResourceProperty
from .resources import IterableT, SearchableT
from .users import User

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
    def add_tag(self, name: str): ...
    def remove_tags(self, name: str): ...

class Tickets(SearchableT[Ticket]):
    RESOURCE_TYPE = Ticket
