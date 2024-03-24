#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, Optional

from .resource import NamedResource, UserListProperty
from .resources import CreatableT, IterableT

if TYPE_CHECKING:
    from .client import Client


class Group(NamedResource):
    """Group(...)"""

    parent: "Groups"  # type: ignore[assignment]

    shared_drafts: bool  #:
    users = UserListProperty()  #:

    @property
    def parent_group(self) -> Optional["Group"]:
        """available since Zammad version 6.2"""
        pid: int = self["parent_id"]
        return None if pid is None else self.parent(pid)


class Groups(IterableT[Group], CreatableT[Group]):
    """Groups(...)"""

    _RESOURCE_TYPE = Group

    def __init__(self, client: "Client"):
        super().__init__(client, "groups")

    def create(self, name: str, **kwargs) -> Group:
        """
        Create a new group.

        :param name: group identifier name
        :param kwargs: additional group properties
        :return: the newly created object
        :rtype: :class:`Group`
        """
        return self._create({"name": name, **kwargs})
