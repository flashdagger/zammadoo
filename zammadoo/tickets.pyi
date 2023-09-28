#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import List

from .organizations import Organization
from .resource import Resource
from .resources import SearchableT
from .ticket_states import TicketState
from .users import User

Article = Resource
Group = Resource
Priority = Resource

class Ticket(Resource):
    articles: Article
    created_at: datetime
    created_by: User
    customer: User
    group: User
    note: str
    number: str
    organization: Organization
    owner: User
    priority: Priority
    state: TicketState
    title: str
    updated_by: User

    _resources: "Tickets"
    def tags(self) -> List[str]: ...
    def add_tag(self, name: str): ...
    def remove_tag(self, name: str): ...

class Tickets(SearchableT[Ticket]):
    RESOURCE_TYPE = Ticket
