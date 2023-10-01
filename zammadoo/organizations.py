#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import Resource
from .resources import SearchableT
from .users import user_property, userlist_property


class Organization(Resource):
    @user_property
    def created_by(self):
        ...

    @user_property
    def updated_by(self):
        ...

    @userlist_property
    def members(self):
        ...


class Organizations(SearchableT[Organization]):
    RESOURCE_TYPE = Organization
