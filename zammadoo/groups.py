#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import NamedResource
from .resources import Creatable, SearchableT
from .users import userlist_property


class Group(NamedResource):
    @userlist_property
    def users(self):
        ...


class Groups(SearchableT[Group], Creatable):
    RESOURCE_TYPE = Group

    create = Creatable._create_with_name

    def __init__(self, client):
        super().__init__(client, "groups")
