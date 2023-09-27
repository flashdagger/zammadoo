#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .resource import Resource
from .resources import SearchableT
from .users import UserProperty


class Organization(Resource):
    created_by = UserProperty()
    updated_by = UserProperty()


class Organizations(SearchableT[Organization]):
    RESOURCE_TYPE = Organization
