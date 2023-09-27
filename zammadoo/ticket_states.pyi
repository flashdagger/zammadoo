#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import Optional

from .resource import Resource, ResourceProperty
from .resources import IterableT
from .users import User

class TicketState(Resource):
    created_by: User
    updated_by: User

class TicketStates(IterableT[TicketState]):
    RESOURCE_TYPE = TicketState

class TicketStateProperty(ResourceProperty[TicketState]):
    def __init__(self, key: Optional[str] = ...) -> None: ...
