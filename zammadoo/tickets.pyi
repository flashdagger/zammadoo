#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .organizations import Organization as Organization
from .resource import Resource
from .resources import SearchableT as SearchableT
from .ticket_states import TicketState
from .users import User as User, UserProperty as UserProperty
from .utils import JsonContainer as JsonContainer
from datetime import datetime

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

class Tickets(SearchableT[Ticket]):
    RESOURCE_TYPE = Ticket
