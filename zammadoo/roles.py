#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, List, TypedDict

from .resource import NamedResource
from .resources import CreatableT, IterableT

if TYPE_CHECKING:
    from .client import Client
    from .groups import Group


class Role(NamedResource):
    """Role(...)"""

    class TypedInfo(TypedDict, total=False):
        permissions: List[str]

    _info: TypedInfo
    default_at_signup: bool  #:

    @property
    def groups(self) -> List["Group"]:
        groups = self.parent.client.groups
        return list(map(groups, self["group_ids"]))

    @property
    def permissions(self) -> List[str]:
        self._initialize(expanded_attribute="permissions")
        return self._info["permissions"]

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
