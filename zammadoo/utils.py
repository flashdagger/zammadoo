#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from itertools import chain
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    TypeVar,
    Union,
    get_args,
)

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from os import PathLike

    from typing_extensions import TypeAlias

    LinkType: TypeAlias = Literal["normal", "parent", "child"]
else:
    LinkType = Literal["normal", "parent", "child"]

LINK_TYPES = get_args(LinkType)

JsonType = Union[None, bool, int, float, str, List["JsonType"], "JsonDict"]
JsonDict = Dict[str, JsonType]
JsonDictList = List[JsonDict]
JsonContainer = Union[JsonDict, JsonDictList]
StringKeyMapping = Mapping[str, Any]
PathType = Union[str, "PathLike[Any]"]


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
    def __init__(
        self,
        info=None,
    ) -> None:
        self._info = info or {}
        self._frozen = True

    def __getattr__(self, name: str) -> Union["JsonType", datetime]:
        info: Dict[str, "JsonType"] = self._info

        if name in info:
            return info[name]

        self._assert_attribute(name)

        if name not in info:
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no attribute {name!r}"
            )

        return info[name]

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
        if name in info:
            return info[name]
        self._assert_attribute(name)
        return info[name]

    def __dir__(self):
        names = super().__dir__()
        extra_attributes = set(self._info.keys()) - set(names)
        return chain(names, extra_attributes)

    def view(self) -> "MappingProxyType[str, JsonType]":
        """
        A mapping view of the objects internal properties as returned by the REST API.

        :rtype: :class:`MappingProxyType[str, Any]`
        """
        self._assert_attribute()
        return MappingProxyType(self._info)


class Property:
    __slots__ = ("name",)

    def __init__(self, name: str = ""):
        self.name = name

    def __set_name__(self, owner, name):
        if not self.name:
            self.name = name


class DateTime(Property):
    def __get__(self, instance, owner=None) -> datetime:
        return datetime.fromisoformat(instance[self.name].replace("Z", "+00:00"))


class OptionalDateTime(Property):
    def __get__(self, instance, owner=None) -> Optional[datetime]:
        value = instance[self.name]
        return (
            None
            if value is None
            else datetime.fromisoformat(instance[self.name].replace("Z", "+00:00"))
        )
