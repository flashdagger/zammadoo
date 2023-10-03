#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from functools import partial
from typing import TYPE_CHECKING

from .resource import NamedResource, resource_property, resourcelist_property
from .resources import Creatable, SearchableT

if TYPE_CHECKING:
    from .organizations import Organization

    _ = Organization


user_property = partial(resource_property("users"))
userlist_property = partial(resourcelist_property("users"))


class User(NamedResource):
    @property
    def name(self):
        name = f"{self.firstname} {self.lastname}".strip()
        if not name:
            name = self.email
        if not name:
            name = self.phone
        return name

    @resourcelist_property
    def groups(self):
        ...

    @resource_property
    def organization(self):
        ...

    @resourcelist_property
    def organizations(self):
        ...

    @resourcelist_property
    def roles(self):
        ...


class Users(SearchableT[User], Creatable):
    RESOURCE_TYPE = User

    def create(
        self, *, firstname=None, lastname=None, email=None, phone=None, **kwargs
    ):
        info = {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "phone": phone,
            **kwargs,
        }
        return self._create(info)

    # pylint: disable=invalid-name
    def me(self) -> User:
        cache = self.cache
        endpoint = "users/me"
        url = f"{self.url()}/{endpoint}"
        callback = partial(self.client.get, endpoint)

        info = cache.setdefault_by_callback(url, callback)
        uid = info["id"]
        cache[self.url(uid)] = info
        return self.RESOURCE_TYPE(self, uid)
