#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
from functools import partial
from typing import TYPE_CHECKING, Optional, cast

from .resource import Resource, ResourceProperty
from .resources import SearchableT

if TYPE_CHECKING:
    from .organizations import Organization

    _ = Organization


class UserProperty(ResourceProperty["User"]):
    def __init__(self, key: Optional[str] = None):
        super().__init__(endpoint="users", key=key or "")


class User(Resource):
    created_by = UserProperty()
    last_login: Optional[datetime.datetime]
    organization = cast("Organization", ResourceProperty("organizations"))


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
