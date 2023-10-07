#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from contextlib import suppress
from datetime import datetime
from functools import wraps
from types import MappingProxyType
from typing import TYPE_CHECKING, Optional

from .utils import JsonDict

if TYPE_CHECKING:
    from .users import User


def resource_property(endpoint, key=None):
    def decorator(_func):
        func_name = _func.__name__
        _key = key or f"{func_name}_id"
        _endpoint = endpoint or f"{func_name}s"

        @property
        @wraps(_func)
        def property_func(self: "Resource"):
            uid = self[_key]
            return uid and getattr(self.parent.client, _endpoint)(uid)

        return property_func

    if isinstance(endpoint, str):
        return decorator

    func, endpoint = endpoint, None
    return decorator(func)


def resourcelist_property(endpoint, key=None):
    def decorator(_func):
        func_name = _func.__name__
        assert func_name.endswith("s")
        _key = key or f"{func_name[:-1]}_ids"
        _endpoint = endpoint or func_name

        @property
        @wraps(_func)
        def propertylist_func(self: "Resource"):
            uids = self[_key]
            return list(map(getattr(self.parent.client, _endpoint), uids))

        return propertylist_func

    if isinstance(endpoint, str):
        return decorator

    func, endpoint = endpoint, None
    return decorator(func)


class Resource:
    def __init__(self, parent, rid, info=None):
        self._id = rid
        self.parent = parent
        self.url = parent.url(rid)
        self._info: JsonDict = info or {}
        self._frozen = True

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.url!r}>"

    def __getattr__(self, item):
        self._initialize()
        info = self._info

        key = item[:-1] if item in {"from_"} else item
        if key not in info:
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no attribute {item!r}"
            )

        value = info[key]
        if isinstance(value, str) and (key.endswith("_at") or key in {"last_login"}):
            with suppress(ValueError):
                return datetime.fromisoformat(value)

        return value

    def __setattr__(self, name, value):
        try:
            self.__getattribute__("_frozen")
        except AttributeError:
            return super().__setattr__(name, value)

        raise AttributeError(
            f"{self.__class__.__name__!r} object attribute {name!r} is read-only"
        )

    def __getitem__(self, item):
        self._initialize()
        return self._info[item]

    def __eq__(self, other):
        return isinstance(other, Resource) and other.url == self.url

    @property
    def id(self) -> int:
        return self._id

    def view(self):
        """
        A mapping view of the objects internal properties as returned by the REST API.

        :rtype: :class:`MappingProxyType[str, Any]`
        """
        self._initialize()
        return MappingProxyType(self._info)

    def _initialize(self):
        if self._info:
            return
        self._info.update(self.parent.cached_info(self._id, refresh=False))

    def reload(self):
        """Updates the object properties by requesting the current data from the server."""
        info = self._info
        info.clear()
        info.update(self.parent.cached_info(self._id), refresh=True)


class MutableResource(Resource):
    created_at: datetime
    updated_at: datetime

    @resource_property("users")
    def created_by(self) -> "User":
        ...

    @resource_property("users")
    def updated_by(self) -> "User":
        ...

    def update(self, **kwargs):
        """
        Update the resource properties.

        :param kwargs: values to be updated (depends on the resource)
        :return: a new instance of the updated resource
        """
        parent = self.parent
        updated_info = parent.client.put(parent.endpoint, self._id, json=kwargs)
        return parent(updated_info["id"], info=updated_info)

    def delete(self):
        """Delete the resource. Requires corresponding permission."""
        parent = self.parent
        parent.client.delete(parent.endpoint, self._id)
        url = self.url
        if url in parent.cache:
            del parent.cache[url]


class NamedResource(MutableResource):
    active: bool
    name: str
    note: Optional[str]
