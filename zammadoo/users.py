#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, List, Optional

from .resource import NamedResource
from .resources import Creatable, SearchableT
from .utils import info_cast

if TYPE_CHECKING:
    from .client import Client
    from .groups import Group
    from .organizations import Organization
    from .roles import Role


class User(NamedResource):
    """User(...)"""

    @property
    def fullname(self) -> str:
        """Users firstname and lastname combined."""
        firstname, lastname = self["firstname"], self["lastname"]
        return f"{firstname}{' ' if firstname and lastname else ''}{lastname}"

    @property
    def name(self) -> str:
        """Alias for users login name."""
        self._initialize()
        return info_cast(self._info)["login"]

    @property
    def groups(self) -> List["Group"]:
        groups = self.parent.client.groups
        return list(map(groups, self["group_ids"]))

    @property
    def organization(self) -> Optional["Organization"]:
        oid = self["organization_id"]
        return oid and self.parent.client.organizations(oid)

    @property
    def organizations(self) -> List["Organization"]:
        organizations = self.parent.client.organizations
        return list(map(organizations, self["organization_ids"]))

    @property
    def roles(self) -> List["Role"]:
        roles = self.parent.client.roles
        return list(map(roles, self["role_ids"]))


class Users(SearchableT[User], Creatable[User]):
    """Users(...)"""

    _RESOURCE_TYPE = User

    def __init__(self, client: "Client"):
        super().__init__(client, "users")

    def create(
        self,
        *,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        **kwargs,
    ) -> "User":
        """
        Create a new zammad user.

        :param firstname:
        :param lastname:
        :param email:
        :param phone:
        :param kwargs: additional user parameter
        """
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
        """
        :return: Return the authenticated user.
        """
        info = self.client.get(self.endpoint, "me")
        return self._RESOURCE_TYPE(self, info["id"], info)
