#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, List, Optional

from .resource import NamedResource
from .resources import CreatableT, IterableT, _T_co

if TYPE_CHECKING:
    from .client import Client
    from .users import User


class Group(NamedResource):
    """Group(...)"""

    shared_drafts: bool  #:
    user_ids: List[int]  #:

    @property
    def parent_group(self: _T_co) -> Optional[_T_co]:
        """available since Zammad version 6.2"""
        pid: int = self["parent_id"]
        return None if pid is None else self.parent(pid)

    @property
    def users(self) -> List["User"]:
        users = self.parent.client.users
        return [users(uid) for uid in self.user_ids]


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
