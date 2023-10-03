#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import List

from .groups import Group
from .resource import NamedResource
from .resources import Creatable, SearchableT

class Role(NamedResource):
    groups: List[Group]
    def update(self, **kwargs) -> "Role": ...

class Roles(SearchableT[Role], Creatable):
    RESOURCE_TYPE = Role
    def create(self, name: str, **kwargs) -> Role: ...
