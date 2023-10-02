#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import List

from .groups import Group
from .resource import NamedResource
from .resources import SearchableT

class Role(NamedResource):
    groups: List[Group]
    def update(self, **kwargs) -> "Role": ...

class Roles(SearchableT[Role]):
    RESOURCE_TYPE = Role
