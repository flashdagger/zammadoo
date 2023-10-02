#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import List

from .resource import NamedResource
from .resources import SearchableT
from .users import User

class Group(NamedResource):
    shared_drafts: bool
    users: List[User]

class Groups(SearchableT[Group]):
    RESOURCE_TYPE = Group
