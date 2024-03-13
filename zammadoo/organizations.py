#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from functools import cached_property
from typing import TYPE_CHECKING, List

from .resource import NamedResource
from .resources import CreatableT, SearchableT

if TYPE_CHECKING:
    from .client import Client
    from .users import User


class Organization(NamedResource):
    """Organization(...)"""

    shared: bool  #:
    domain: str  #:
    domain_assignment: bool  #:

    @property
    def members(self) -> List["User"]:
        users = self.parent.client.users
        return list(map(users, self["member_ids"]))

    @property
    def secondary_members(self) -> List["User"]:
        users = self.parent.client.users
        return list(map(users, self["secondary_member_ids"]))

    @cached_property
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
