#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Callable, Optional

from .organizations import Organization
from .resource import UpdatableResource
from .resources import SearchableT

user_property: Callable[..., "User"]
userlist_property: Callable[..., "User"]

class User(UpdatableResource):
    email: str
    firstname: str
    last_login: Optional[datetime]
    lastname: str
    organization: Optional[Organization]

class Users(SearchableT[User]):
    RESOURCE_TYPE = User
    def me(self) -> User: ...
