#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, List

from .resource import NamedResource
from .resources import Creatable, SearchableT

if TYPE_CHECKING:
    from .client import Client
    from .groups import Group


class Role(NamedResource):
    """Role(...)"""

    @property
    def groups(self) -> List["Group"]:
        groups = self.parent.client.groups
        return list(map(groups, self["group_ids"]))

    def delete(self):
        """
        Since roles cannot be deletet via REST API, this method is not Implemented

        :raises: :exc:`NotImplementedError`
        """
        raise NotImplementedError("roles cannot be deletet via REST API")


class Roles(SearchableT[Role], Creatable[Role]):
    """Roles(...)"""

    _RESOURCE_TYPE = Role

    def __init__(self, client: "Client"):
        super().__init__(client, "roles")

    create = Creatable.create_with_name
