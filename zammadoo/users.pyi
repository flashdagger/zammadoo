#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Callable, List, Optional

from .client import Client
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
    phone: str
    roles: List[Role]
    def update(self, **kwargs) -> "User": ...

class Users(SearchableT[User]):
    RESOURCE_TYPE = User
    def __init__(self, client: Client) -> None: ...
    def create(
        self,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        **kwargs,
    ) -> User: ...
    def me(self) -> User: ...
