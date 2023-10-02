#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import NamedResource, resourcelist_property
from .resources import SearchableT


class Role(NamedResource):
    @resourcelist_property
    def groups(self):
        ...


class Roles(SearchableT[Role]):
    RESOURCE_TYPE = Role
