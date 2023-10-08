#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from os import PathLike
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    TypedDict,
    TypeVar,
    Union,
    cast,
    get_args,
)

from typing_extensions import TypeAlias

LINK_TYPE: TypeAlias = Literal["normal", "parent", "child"]
LINK_TYPES = get_args(LINK_TYPE)

JsonType = Union[None, bool, int, float, str, List["JsonType"], "JsonDict"]
JsonDict = Dict[str, JsonType]
JsonDictList = List[JsonDict]
JsonContainer = Union[JsonDict, JsonDictList]
StringKeyDict = Dict[str, Any]
PathType = Union[str, PathLike]


class TypedInfo(TypedDict, total=False):
    id: int
    name: str
    login: str
    preferences: Dict[str, str]


def info_cast(info: "JsonDict") -> TypedInfo:
    """
    convenience function when using items from the info dictionary
    that nedd to have a certain type
    """
    return cast(TypedInfo, info)


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
