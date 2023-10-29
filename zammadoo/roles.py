#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, List

from .resource import NamedResource
from .resources import CreatableT, IterableT
from .utils import info_cast

if TYPE_CHECKING:
    from .client import Client
    from .groups import Group


class Role(NamedResource):
    """Role(...)"""

    default_at_signup: bool  #:

    @property
    def groups(self) -> List["Group"]:
        groups = self.parent.client.groups
        return list(map(groups, self["group_ids"]))

    @property
    def permissions(self) -> List[str]:
        info = self._info
        if "permissions" not in info:
            self.reload(expand=True)
        return info_cast(info)["permissions"]

    def delete(self):
        """
        Since roles cannot be deletet via REST API, this method is not Implemented

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
