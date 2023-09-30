#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import Optional

from .resource import Resource, ResourceListProperty, ResourceProperty
from .resources import SearchableT
from .users import UserListProperty, UserProperty


class Organization(Resource):
    created_by = UserProperty()
    updated_by = UserProperty()
    members = UserListProperty()


class Organizations(SearchableT[Organization]):
    RESOURCE_TYPE = Organization


class OrganizationProperty(ResourceProperty[Organization]):
    def __init__(self, key: Optional[str] = None):
        super().__init__(endpoint="organizations", key=key or "")


class OrganizationListProperty(ResourceListProperty[Organization]):
    def __init__(self, key: Optional[str] = None):
        super().__init__(endpoint="organizations", key=key or "")
