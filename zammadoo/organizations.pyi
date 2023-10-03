#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import List

from .resource import MutableResource
from .resources import SearchableT
from .users import User

class Organization(MutableResource):
    domain: str
    domain_assignment: bool
    members: List[User]
    shared: bool
    vip: bool
    def update(self, **kwargs) -> "Organization": ...

class Organizations(SearchableT[Organization]):
    RESOURCE_TYPE = Organization
    def create(self, name: str, **kwargs) -> Organization: ...
