#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import MutableResource
from .resources import SearchableT
from .users import userlist_property


class Organization(MutableResource):
    @userlist_property
    def members(self):
        ...


class Organizations(SearchableT[Organization]):
    RESOURCE_TYPE = Organization
