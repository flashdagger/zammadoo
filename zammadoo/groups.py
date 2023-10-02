#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import NamedResource
from .resources import SearchableT
from .users import userlist_property


class Group(NamedResource):
    @userlist_property
    def users(self):
        ...


class Groups(SearchableT[Group]):
    RESOURCE_TYPE = Group
