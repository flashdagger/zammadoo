#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, Dict, List, Optional, Union

from .groups import Group
from .resource import NamedResource, OptionalUserProperty
from .resources import CreatableT, SearchableT
from .utils import AttributeT, OptionalDateTime

if TYPE_CHECKING:
    from .client import Client
    from .organizations import Organization
    from .resource import TypedResourceDict
    from .roles import Role


class User(NamedResource):
    """User(...)"""

    EXPANDED_ATTRIBUTES = (
        "authorizations",
        "created_by",
        "groups",
        "organizations",
        "overview_sortings",
        "roles",
        "two_factor_preferences",
        "updated_by",
    )

    department: Optional[str]  #:
    email: str  #:
    fax: str  #:
    firstname: str  #:
    image: Optional[str]  #:
    last_login = OptionalDateTime()
    lastname: str  #:
    login: str  #: users login name
    login_failed: int  #:
    mobile: str  #:
    name = AttributeT[str]("login")  #: alias for :attr:`login`
    out_of_office: bool  #:
    out_of_office_end_at = OptionalDateTime()
    out_of_office_replacement = OptionalUserProperty()
    out_of_office_start_at = OptionalDateTime()
    parent: "Users"
    phone: str  #:
    verified: bool  #:
    vip: bool  #:
    web: str  #:

    @property
    def fullname(self) -> str:
        """users firstname and lastname combined, or email"""
        fullname = " ".join(filter(bool, (self["firstname"], self["lastname"])))
        return fullname or self["email"]

    @property
    def longname(self) -> str:
        """users fullname with organization"""
        fullname = self.fullname
        organization = self.organization
        return f"{fullname} ({organization.name})" if organization else fullname

    @property
    def groups(self) -> List[Group]:
        groups = self.parent.client.groups
        return [groups(int(gid)) for gid in self["group_ids"]]

    @property
    def organization(self) -> Optional["Organization"]:
        oid: Optional[int] = self["organization_id"]
        return None if oid is None else self.parent.client.organizations(oid)

    @property
    def organizations(self) -> List["Organization"]:
        organizations = self.parent.client.organizations
        return [organizations(oid) for oid in self["organization_ids"]]

    @property
    def roles(self) -> List["Role"]:
        roles = self.parent.client.roles
        return [roles(rid) for rid in self["role_ids"]]

    @property
    def weburl(self) -> str:
        """URL of the user profile in the webclient"""
        return f"{self.parent.client.weburl}/#user/profile/{self.id}"

    def group_access(self, group: Union[int, Group]) -> List[str]:
        """
        :param group: group object or group id
        :return: a list of all access rights for a given group
        """
        if isinstance(group, Group):
            group = group.id
        groups: Dict[str, List[str]] = self["group_ids"]
        return groups.get(str(group), [])


class Users(SearchableT[User], CreatableT[User]):
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

        :param firstname: users first name
        :param lastname: users last name
        :param email: users email address
        :param phone: users phone number
        :param kwargs: additional user properties
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
        info: "TypedResourceDict" = self.client.get(
            self.endpoint, "me", _erase_return_type=True
        )
        return self._RESOURCE_TYPE(self, info["id"], info=info)
