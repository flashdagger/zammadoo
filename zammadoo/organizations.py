#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING

from .resource import NamedResource, UserListProperty
from .resources import CreatableT, SearchableT

if TYPE_CHECKING:
    from .client import Client


class Organization(NamedResource):
    """Organization(...)"""

    EXPANDED_ATTRIBUTES = ("created_by", "members", "updated_by")

    domain: str  #:
    domain_assignment: bool  #:
    members = UserListProperty()  #:
    parent: "Organizations"
    secondary_members = UserListProperty()  #:
    shared: bool  #:

    @property
    def weburl(self) -> str:
        """URL of the organization profile in the webclient"""
        return f"{self.parent.client.weburl}/#organization/profile/{self.id}"


class Organizations(SearchableT[Organization], CreatableT[Organization]):
    """Organizations(...)"""

    _RESOURCE_TYPE = Organization

    def __init__(self, client: "Client"):
        super().__init__(client, "organizations")

    def create(self, name: str, **kwargs) -> Organization:
        """
        Create a new organization.

        :param name: organization identifier name
        :param kwargs: additional organization properties
        :return: the newly created object
        :rtype: :class:`Organization`
        """
        return self._create({"name": name, **kwargs})
