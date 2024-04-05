#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
from datetime import datetime
from itertools import chain
from types import MappingProxyType
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

JsonType = Union[None, bool, int, float, str, List["JsonType"], "JsonDict"]
JsonDict = Dict[str, JsonType]
StringKeyMapping = Mapping[str, Any]
JsonMapping = Union[JsonDict, Iterable[Tuple[str, JsonType]]]


class YieldCounter:
    _T = TypeVar("_T")

    def __init__(self) -> None:
        self._counter = 0

    @property
    def yielded(self):
        return self._counter

    def __call__(self, itr: Iterable[_T]) -> Iterable[_T]:
        self._counter = 0
        for count, item in enumerate(itr, 1):
            self._counter = count
            yield item


class FrozenInfo:
    __slots__ = ("_info", "_frozen")

    def __init__(
        self,
        info: JsonMapping,
    ) -> None:
        self._info = dict(info)
        self._frozen = True

    def __getattr__(self, name: str) -> "JsonType":
        info: Dict[str, "JsonType"] = self._info

        try:
            return info[name]
        except KeyError:
            self._assert_attribute(name)

        if name in info:
            return info[name]

        raise AttributeError(
            f"{self.__class__.__name__!r} object has no attribute {name!r}"
        )

    def _assert_attribute(self, name: Optional[str] = None) -> None:
        pass

    def __setattr__(self, name: str, value: Any) -> None:
        try:
            self.__getattribute__("_frozen")
        except AttributeError:
            return super().__setattr__(name, value)

        raise AttributeError(f"object {self.__class__.__name__!r} is read-only")

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"object {self.__class__.__name__!r} is read-only")

    def __getitem__(self, name: str) -> Any:
        info = self._info
        try:
            return info[name]
        except KeyError:
            self._assert_attribute(name)
        return info[name]

    def __dir__(self):
        names = super().__dir__()
        extra_attributes = set(self._info.keys()) - set(names)
        return chain(names, extra_attributes)

    def view(self) -> "StringKeyMapping":
        """
        returns a mapping view of the objects internal properties
        as returned by the REST API.
        """
        self._assert_attribute()
        return MappingProxyType(self._info)


class _AttributeBase:
    __slots__ = ("name",)

    def __init__(self, name: str = ""):
        self.name = name

    def __set_name__(self, owner, name):
        if not self.name:
            self.name = name


_T = TypeVar("_T")


class AttributeT(_AttributeBase, Generic[_T]):
    def __get__(self, instance, owner=None) -> _T:
        value: _T = instance[self.name]
        return value


_fromisoformat = datetime.fromisoformat

if sys.version_info < (3, 11):

    def convert_date(date_string: str) -> datetime:
        return _fromisoformat(date_string.replace("Z", "+00:00"))

else:
    convert_date = _fromisoformat


class DateTime(_AttributeBase):
    def __get__(self, instance, owner=None) -> datetime:
        return convert_date(instance[self.name])


class OptionalDateTime(_AttributeBase):
    def __get__(self, instance, owner=None) -> Optional[datetime]:
        value = instance[self.name]
        return None if value is None else convert_date(instance[self.name])
