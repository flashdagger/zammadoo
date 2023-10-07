#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import MutableResource
from .resources import Creatable, SearchableT
from .users import userlist_property


class Organization(MutableResource):
    @userlist_property
    def members(self):
        ...


class Organizations(SearchableT[Organization], Creatable):
    RESOURCE_TYPE = Organization
    create = Creatable.create_with_name

    def __init__(self, client):
        super().__init__(client, "organizations")
