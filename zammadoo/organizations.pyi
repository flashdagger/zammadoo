#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import List, Optional

from .resource import Resource as Resource
from .resource import ResourceListProperty, ResourceProperty
from .resources import SearchableT
from .users import User

class Organization(Resource):
    created_by: User
    members: List[User]
    updated_by: User

class Organizations(SearchableT[Organization]):
    RESOURCE_TYPE = Organization

class OrganizationProperty(ResourceProperty[Organization]):
    def __init__(self, key: Optional[str] = ...) -> None: ...

class OrganizationListProperty(ResourceListProperty[Organization]):
    def __init__(self, key: Optional[str] = ...) -> None: ...
