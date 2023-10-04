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
    def fullname(self):
        firstname, lastname = self["firstname"], self["lastname"]
        return f"{firstname}{' ' if firstname and lastname else ''}{lastname}"

    @property
    def name(self):
        return self["email"] or self["phone"]

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

    def __init__(self, client):
        super().__init__(client, "users")

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
        return super()._create(info)

    # pylint: disable=invalid-name
    def me(self) -> User:
        info = self.client.get(self.endpoint, "me")
        return self.RESOURCE_TYPE(self, info["id"], info)
