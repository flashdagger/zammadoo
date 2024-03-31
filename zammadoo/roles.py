#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, List

from .resource import NamedResource
from .resources import CreatableT, IterableT

if TYPE_CHECKING:
    from .client import Client
    from .groups import Group


class Role(NamedResource):
    """Role(...)"""

    EXPANDED_ATTRIBUTES = (
        "created_by",
        "groups",
        "knowledge_base_permissions",
        "permissions",
        "updated_by",
    )

    default_at_signup: bool  #:
    knowledge_base_permissions: List[str]  #:
    parent: "Roles"
    permissions: List[str]  #:

    @property
    def groups(self) -> List["Group"]:
        groups = self.parent.client.groups
        return [groups(gid) for gid in self["group_ids"]]

    def delete(self):
        """
        Since roles cannot be deletet via REST API, this method is not implemented

        :raises: :exc:`NotImplementedError`
        """
        raise NotImplementedError("roles cannot be deletet via REST API")


class Roles(IterableT[Role], CreatableT[Role]):
    """Roles(...)"""

    _RESOURCE_TYPE = Role

    def __init__(self, client: "Client"):
        super().__init__(client, "roles")

    def create(self, name: str, **kwargs) -> Role:
        """
        Create a new role.

        :param name: role identifier name
        :param kwargs: additional role properties
        :return: the newly created object
        :rtype: :class:`Role`
        """
        return self._create({"name": name, **kwargs})
