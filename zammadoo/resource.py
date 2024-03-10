#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from contextlib import suppress
from datetime import datetime
from itertools import chain
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Optional

from .resources import ResourcesT, _T_co
from .utils import fromisoformat, info_cast

if TYPE_CHECKING:
    from .users import User
    from .utils import JsonDict, JsonType


class Resource:
    def __init__(
        self: _T_co,
        parent: ResourcesT[_T_co],
        rid: int,
        info: Optional["JsonDict"] = None,
    ) -> None:
        self._id = rid
        self.parent = parent
        self._url = f"{parent.url}/{rid}"
        self._info: "JsonDict" = info or {}
        self._frozen = True

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.url!r}>"

    def __getattr__(self, name: str) -> object:
        self._initialize()
        info = self._info

        key = name[:-1] if name in {"from_"} else name
        if key not in info:
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no attribute {name!r}"
            )

        value = info[key]
        if isinstance(value, str) and key.endswith("_at"):
            with suppress(ValueError):
                return fromisoformat(value)

        return value

    def __setattr__(self, name: str, value: Any) -> None:
        try:
            self.__getattribute__("_frozen")
        except AttributeError:
            return super().__setattr__(name, value)

        raise AttributeError(f"object {self.__class__.__name__!r} is read-only")

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"object {self.__class__.__name__!r} is read-only")

    def __getitem__(self, name: str) -> Any:
        self._initialize()
        return self._info[name]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Resource) and other.url == self.url

    def __dir__(self):
        names = super().__dir__()
        extra_attributes = set(self._info.keys()) - set(names)
        return chain(names, extra_attributes)

    @property
    def id(self) -> int:
        return self._id

    @property
    def url(self) -> str:
        """the API endpoint URL"""
        return self._url

    def view(self) -> "MappingProxyType[str, JsonType]":
        """
        A mapping view of the objects internal properties as returned by the REST API.

        :rtype: :class:`MappingProxyType[str, Any]`
        """
        self._initialize()
        return MappingProxyType(self._info)

    def _initialize(self, expanded_attribute: Optional[str] = None) -> None:
        info = self._info
        expand = expanded_attribute and expanded_attribute not in info
        refresh = info and expand

        if refresh:
            info.clear()

        if expand or not info:
            cached_info = self.parent.cached_info(
                self._id, refresh=refresh, expand=expand
            )
            info.update(cached_info)

    def reload(self, expand=False) -> None:
        """
        Update the object properties by requesting the current data from the server.

        :param expand: if ``True`` the properties will contain `additional information
               <https://docs.zammad.org/en/latest/api/intro.html#response-payloads-expand>`_.
        """
        info = self._info
        info.clear()
        new_info = self.parent.cached_info(self._id, refresh=True, expand=expand)
        info.update(new_info)

    def last_request_at(self) -> Optional[datetime]:
        """return the last request timestamp as :class:`datetime` or ``None``"""
        return self.parent.cached_timestamp(self._id)


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
        updated_info = parent.client.put(parent.endpoint, self._id, json=kwargs)
        return parent(updated_info["id"], info=updated_info)

    def delete(self) -> None:
        """Delete the resource. Requires the respective permission."""
        self.parent.delete(self._id)


class NamedResource(MutableResource):
    active: bool  #:
    note: Optional[str]  #:

    @property
    def name(self) -> str:
        self._initialize()
        return info_cast(self._info)["name"]
