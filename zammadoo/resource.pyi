#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from types import MappingProxyType
from typing import Callable, Optional, TypeVar

from .resources import ResourcesT
from .users import User
from .utils import JsonDict, JsonType

T = TypeVar("T", bound="Resource")

def resource_property(endpoint, key: Optional[str] = ...) -> Callable: ...
def resourcelist_property(endpoint, key: Optional[str] = ...) -> Callable: ...

class Resource:
    def __init__(
        self, resources: ResourcesT, rid: int, info: Optional[JsonDict] = ...
    ) -> None: ...
    def __getattr__(self, item: str): ...
    def __getitem__(self, item: str): ...
    def __eq__(self, other): ...
    @property
    def id(self) -> int: ...
    def view(self) -> MappingProxyType[str, JsonType]: ...
    def reload(self) -> None: ...

class MutableResource(Resource):
    created_by: User
    updated_by: User
    created_at: datetime
    updated_at: datetime
    def update(self, **kwargs): ...
    def delete(self) -> None: ...

class NamedResource(MutableResource):
    active: bool
    name: str
    note: str
