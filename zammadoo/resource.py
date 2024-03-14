#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional, Tuple

from .resources import ResourcesT, _T_co
from .utils import FrozenInfo

if TYPE_CHECKING:
    from .users import User
    from .utils import JsonDict


class Resource(FrozenInfo):
    EXPANDED_ATTRIBUTES: Tuple[str, ...] = ()

    id: int  #:
    url: str  #: the API endpoint URL

    def __init__(
        self: _T_co,
        parent: ResourcesT[_T_co],
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
        expand = (
            name is not None and name in self.EXPANDED_ATTRIBUTES and name not in info
        )
        if expand or not info:
            cached_info = self.parent.cached_info(
                self.id, refresh=(info and expand), expand=expand
            )
            info.clear()
            info.update(cached_info)

    def reload(self, expand=False) -> None:
        """
        Update the object properties by requesting the current data from the server.

        :param expand: if ``True`` the properties will contain `additional information
               <https://docs.zammad.org/en/latest/api/intro.html#response-payloads-expand>`_.
        """
        info = self._info
        info.clear()
        new_info = self.parent.cached_info(self.id, refresh=True, expand=expand)
        info.update(new_info)

    def last_request_at(self) -> Optional[datetime]:
        """return the last request timestamp as :class:`datetime` or ``None``"""
        return self.parent.cached_timestamp(self.id)


class MutableResource(Resource):
    created_at: datetime  #:
    updated_at: datetime  #:

    @property
    def created_by(self) -> "User":
        uid = self["created_by_id"]
        return self.parent.client.users(uid)

    @property
    def updated_by(self) -> "User":
        uid = self["updated_by_id"]
        return self.parent.client.users(uid)

    def update(self: _T_co, **kwargs) -> _T_co:
        """
        Update the resource properties.

        :param kwargs: values to be updated (depending on the resource)
        :return: a new instance of the updated resource
        :rtype: same as object
        """
        parent = self.parent
        updated_info = parent.client.put(parent.endpoint, self.id, json=kwargs)
        return parent(updated_info["id"], info=updated_info)

    def delete(self) -> None:
        """Delete the resource. Requires the respective permission."""
        self.parent.delete(self.id)


class NamedResource(MutableResource):
    active: bool  #:
    name: str  #:
    note: Optional[str]  #:
