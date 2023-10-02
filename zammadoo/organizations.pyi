#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import List

from .resource import MutableResource
from .resources import SearchableT
from .users import User

class Organization(MutableResource):
    members: List[User]
    shared: bool
    domain_assignment: bool
    vip: bool
    def update(self, **kwargs) -> "Organization": ...

class Organizations(SearchableT[Organization]):
    RESOURCE_TYPE = Organization
