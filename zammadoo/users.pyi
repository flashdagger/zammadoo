#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Callable, List, Optional

from .groups import Group
from .organizations import Organization
from .resource import NamedResource
from .resources import SearchableT
from .roles import Role

user_property: Callable[..., "User"]
userlist_property: Callable[..., "User"]

class User(NamedResource):
    email: str
    firstname: str
    groups: List[Group]
    last_login: Optional[datetime]
    lastname: str
    organization: Optional[Organization]
    organizations: List[Organization]
    roles: List[Role]
    def update(self, **kwargs) -> "User": ...

class Users(SearchableT[User]):
    RESOURCE_TYPE = User
    def me(self) -> User: ...
