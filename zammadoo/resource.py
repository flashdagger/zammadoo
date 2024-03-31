#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union

from .resources import ResourcesT, _T_co
from .utils import DateTime, FrozenInfo, _AttributeBase

if TYPE_CHECKING:
    from typing import Literal, overload

    from .users import User
    from .utils import AttributeT, JsonDict, JsonType

    class TypedResourceDict(JsonDict):
        @overload
        def __getitem__(self, item: Literal["id"]) -> int: ...

        @overload
        def __getitem__(self, item: str) -> "JsonType": ...

        def __getitem__(self, item): ...


class Resource(FrozenInfo):
    EXPANDED_ATTRIBUTES: Tuple[str, ...] = ()  #: :meta private:

    id: int  #:
    url: str  #: the API endpoint URL

    def __init__(
        self,
        parent: ResourcesT[Any],
        rid: int,
        *,
        info: Optional["JsonDict"] = None,
    ) -> None:
        self.id = rid
        self.parent = parent
        self.url = f"{parent.url}/{rid}"
        super().__init__(info)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.url!r}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Resource) and other.url == self.url

    def _assert_attribute(self, name: Optional[str] = None) -> None:
        info = self._info
        if name is None:
            name = "id"

        if name in info:
            return

        expanded_attributes = self.EXPANDED_ATTRIBUTES
        name_in_expanded_attributes = name in expanded_attributes
        refresh = info and name_in_expanded_attributes
        cached_info = self.parent.cached_info(
            self.id,
            refresh=refresh,
            expand=(name_in_expanded_attributes or "*" in expanded_attributes),
        )
        if name_in_expanded_attributes and not refresh and name not in cached_info:
            cached_info = self.parent.cached_info(self.id, refresh=True, expand=True)
        info.clear()
        info.update(cached_info)

    def reload(self, expand=False) -> None:
        """
        Update the object properties by requesting the current data from the server.

        :param expand: if ``True`` the properties will contain `additional information
               <https://docs.zammad.org/en/latest/api/intro.html#response-payloads-expand>`_.

        .. note::
           if :attr:`EXPANDED_ATTRIBUTES` contains ``'*'`` **expand** will always be ``True``

        """
        info = self._info
        info.clear()
        new_info = self.parent.cached_info(
            self.id, refresh=True, expand=expand or "*" in self.EXPANDED_ATTRIBUTES
        )
        info.update(new_info)

    def last_request_at(self) -> Optional[datetime]:
        """:return: the last request timestamp"""
        return self.parent.cache.timestamp(self.url)


class UserProperty(_AttributeBase):
    def __get__(self, instance: Resource, owner=None) -> "User":
        return instance.parent.client.users(instance[f"{self.name}_id"])


class UserListProperty(_AttributeBase):
    def __get__(self, instance: Resource, owner=None) -> List["User"]:
        user = instance.parent.client.users
        uids = instance[f"{self.name[:-1]}_ids"]
        return [user(uid) for uid in uids]


class OptionalUserProperty(_AttributeBase):
    def __get__(self, instance: Resource, owner=None) -> Optional["User"]:
        value = instance[f"{self.name}_id"]
        return None if value is None else instance.parent.client.users(value)


class MutableResource(Resource):
    created_at = DateTime()
    created_by = UserProperty()
    updated_at = DateTime()
    updated_by = UserProperty()

    def update(self: _T_co, **kwargs) -> _T_co:
        """
        Update the resource properties.

        :param kwargs: values to be updated (depending on the resource)
        :return: a new instance of the updated resource
        :rtype: same as object
        """
        parent = self.parent
        updated_info = parent.client.put(parent.endpoint, self.id, json=kwargs)
        updated_resource: _T_co = parent(updated_info["id"], info=updated_info)
        return updated_resource

    def delete(self) -> None:
        """Delete the resource. Requires the respective permission."""
        self.parent.delete(self.id)


class NamedResource(MutableResource):
    active: bool  #:
    name: Union[str, "AttributeT[str]"]  #:
    note: Optional[str]  #:
