#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import NamedResource, resourcelist_property
from .resources import SearchableT, Creatable


class Role(NamedResource):
    @resourcelist_property
    def groups(self):
        ...

    def delete(self):
        raise NotImplementedError("roles cannot be deletet via REST API")


class Roles(SearchableT[Role], Creatable):
    RESOURCE_TYPE = Role
    create = Creatable._create_with_name
