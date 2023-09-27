#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
from typing import Optional, Iterable

from .organizations import Organization as Organization
from .resource import Resource, ResourceProperty
from .resources import SearchableT

class UserProperty(ResourceProperty["User"]):
    def __init__(self, key: Optional[str] = ...) -> None: ...

class User(Resource):
    created_by: User
    last_login: Optional[datetime.datetime]
    organization: Organization

class Users(SearchableT[User]):
    RESOURCE_TYPE = User
    def me(self) -> User: ...
