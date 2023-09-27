#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import Resource, ResourceProperty
from .resources import IterableT
from .users import UserProperty


class TicketState(Resource):
    created_by = UserProperty()
    updated_by = UserProperty()


class TicketStates(IterableT[TicketState]):
    RESOURCE_TYPE = TicketState


class TicketStateProperty(ResourceProperty[TicketState]):
    def __init__(self, key=None):
        super().__init__(endpoint="ticket_states", key=key or "")
