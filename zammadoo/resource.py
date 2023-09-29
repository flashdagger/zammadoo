#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from contextlib import suppress
from datetime import datetime
from types import MappingProxyType
from typing import TYPE_CHECKING, Generic, List, Optional, Type, TypeVar

from .utils import JsonDict

if TYPE_CHECKING:
    from .resources import BaseResources, ResourcesT


class Resource:
    def __init__(
        self, resources: "ResourcesT", rid: int, info: Optional[JsonDict] = None
    ):
        self._id = rid
        self._resources = resources
        self._info: JsonDict = info or {}

    def __repr__(self):
        url = self._resources.url(self.id)
        return f"<{self.__class__.__qualname__} {url!r}>"

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

    @property
    def id(self):
        return self._id

    def view(self):
        self._initialize()
        return MappingProxyType(self._info)

    def _initialize(self):
        if self._info:
            return
        self._info.update(self._resources.get(self._id, refresh=False))

    def reload(self):
        info = self._info
        info.clear()
        info.update(self._resources.get(self._id), refresh=True)


T = TypeVar("T", bound=Resource)


class ResourceProperty(Generic[T]):
    def __init__(self, endpoint="", key=""):
        self.endpoint = endpoint
        self.key = key

    def __set_name__(self, owner: Type[Resource], name: str):
        self.key = f"{name}_id"
        if not self.endpoint:
            self.endpoint = f"{name}s"

    def __get__(self, instance: Resource, owner: Type[Resource]) -> T:
        rid = instance[self.key]
        resources: ResourcesT[T] = getattr(instance, "_resources")
        return rid and getattr(resources.client, self.endpoint)(rid)


class ResourceListProperty(Generic[T]):
    def __init__(self, endpoint="", key=""):
        self.endpoint = endpoint
        self.key = key

    def __set_name__(self, owner, name):
        assert name.endswith("s")
        self.key = f"{name[:-1]}_ids"
        if not self.endpoint:
            self.endpoint = name

    def __get__(self, instance: Resource, owner: Type[Resource]) -> List[T]:
        rids = instance[self.key]
        instance_resources: BaseResources = getattr(instance, "_resources")
        resources: ResourcesT[T] = getattr(instance_resources.client, self.endpoint)
        return [resources(rid) for rid in rids]
