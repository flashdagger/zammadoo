#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import List

from .resource import UpdatableResource
from .resources import SearchableT
from .users import User

class Organization(UpdatableResource):
    members: List[User]

class Organizations(SearchableT[Organization]):
    RESOURCE_TYPE = Organization
