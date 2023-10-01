#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import UpdatableResource
from .resources import SearchableT
from .users import userlist_property


class Group(UpdatableResource):
    @userlist_property
    def users(self):
        ...


class Groups(SearchableT[Group]):
    RESOURCE_TYPE = Group
