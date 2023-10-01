#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from functools import partial
from typing import TYPE_CHECKING

from .resource import Resource, resource_property, resourcelist_property
from .resources import SearchableT

if TYPE_CHECKING:
    from .organizations import Organization

    _ = Organization


user_property = partial(resource_property("users"))
userlist_property = partial(resourcelist_property("users"))


class User(Resource):
    @user_property
    def created_by(self):
        ...

    @resource_property
    def organization(self):
        ...


class Users(SearchableT[User]):
    RESOURCE_TYPE = User

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
