#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import List

from . import Client
from .resource import NamedResource
from .resources import SearchableT
from .users import User

class Group(NamedResource):
    shared_drafts: bool
    users: List[User]
    def update(self, **kwargs) -> "Group": ...

class Groups(SearchableT[Group]):
    RESOURCE_TYPE = Group
    def __init__(self, client: Client) -> None: ...
    def create(self, name: str, **kwargs) -> Group: ...
