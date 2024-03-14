#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, List, Optional, TypedDict

from .resource import NamedResource
from .resources import CreatableT, IterableT, _T_co

if TYPE_CHECKING:
    from .client import Client
    from .users import User


class Group(NamedResource):
    """Group(...)"""

    class TypedInfo(TypedDict, total=False):
        parent_id: Optional[int]
        user_ids: List[int]

    _info: TypedInfo
    shared_drafts: bool  #:

    @property
    def parent_group(self: _T_co) -> Optional[_T_co]:
        """available since Zammad version 6.2"""
        self._initialize()
        pid = self._info.get("parent_id")
        return self.parent(pid) if pid is not None else None

    @property
    def users(self) -> List["User"]:
        self._initialize()
        uids = self._info["user_ids"]
        return list(map(self.parent.client.users, uids))


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
