#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import TYPE_CHECKING, List

from .resource import NamedResource
from .resources import Creatable, SearchableT

if TYPE_CHECKING:
    from .client import Client
    from .users import User


class Group(NamedResource):
    shared_drafts: bool  #:

    @property
    def users(self) -> List["User"]:
        users = self.parent.client.users
        return list(map(users, self["user_ids"]))


class Groups(SearchableT[Group], Creatable[Group]):
    RESOURCE_TYPE = Group

    create = Creatable.create_with_name

    def __init__(self, client: "Client"):
        super().__init__(client, "groups")
