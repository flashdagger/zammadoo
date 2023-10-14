#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, List

from .resource import MutableResource
from .resources import Creatable, SearchableT

if TYPE_CHECKING:
    from .client import Client
    from .users import User


class Organization(MutableResource):
    """Organization(...)"""

    @property
    def members(self) -> List["User"]:
        users = self.parent.client.users
        return list(map(users, self["member_ids"]))


class Organizations(SearchableT[Organization], Creatable[Organization]):
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
