#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from contextlib import suppress
from datetime import datetime
from functools import wraps
from types import MappingProxyType
from typing import TYPE_CHECKING, Optional, TypeVar

from .utils import JsonDict

if TYPE_CHECKING:
    from .resources import ResourcesT

T = TypeVar("T", bound="Resource")


def resource_property(endpoint, key=None):
    def decorator(_func):
        func_name = _func.__name__
        _key = key or f"{func_name}_id"
        _endpoint = endpoint or f"{func_name}s"

        @property
        @wraps(_func)
        def property_func(self: "Resource"):
            uid = self[_key]
            client = getattr(self, "_resources").client
            return uid and getattr(client, _endpoint)(uid)

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
            client = getattr(self, "_resources").client
            return list(map(getattr(client, _endpoint), uids))

        return propertylist_func

    if isinstance(endpoint, str):
        return decorator

    func, endpoint = endpoint, None
    return decorator(func)


class Resource:
    def __init__(
        self, resources: "ResourcesT", rid: int, info: Optional[JsonDict] = None
    ):
        self._id = rid
        self._resources = resources
        self._info: JsonDict = info or {}
        self.url = resources.url(rid)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.url!r}>"

    def __getattr__(self, item: str):
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

    def __getitem__(self, item: str):
        self._initialize()
        return self._info[item]

    def __eq__(self, other):
        return isinstance(other, Resource) and other.url == self.url

    @property
    def id(self):
        return self._id

    def view(self):
        self._initialize()
        return MappingProxyType(self._info)

    def _initialize(self):
        if self._info:
            return
        self._info.update(self._resources.cached_info(self._id, refresh=False))

    def reload(self):
        info = self._info
        info.clear()
        info.update(self._resources.cached_info(self._id), refresh=True)


class MutableResource(Resource):
    @resource_property("users")
    def created_by(self):
        ...

    @resource_property("users")
    def updated_by(self):
        ...

    def update(self, **kwargs):
        resources = self._resources
        updated_info = resources.client.put(resources.endpoint, self._id, json=kwargs)
        return resources(updated_info["id"], info=updated_info)

    def delete(self):
        resources = self._resources
        resources.client.delete(resources.endpoint, self._id)
        url = self.url
        if url in resources.cache:
            del resources.cache[url]


class NamedResource(MutableResource):
    pass
