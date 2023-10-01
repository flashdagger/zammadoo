#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import List

from .resource import Resource
from .resources import SearchableT
from .users import User

class Organization(Resource):
    created_by: User
    members: List[User]
    updated_by: User

class Organizations(SearchableT[Organization]):
    RESOURCE_TYPE = Organization
