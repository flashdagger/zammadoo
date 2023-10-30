#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from os import PathLike
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    TypedDict,
    TypeVar,
    Union,
    cast,
    get_args,
)

if TYPE_CHECKING:
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
PathType = Union[str, PathLike]


class TypedTag(TypedDict):
    id: int
    name: str
    count: Optional[int]


class TypedInfo(TypedDict, total=False):
    create_article_sender: str
    create_article_type: str
    id: int
    name: str
    login: str
    preferences: Dict[str, str]
    page: int
    per_page: int
    permissions: List[str]
    tags: List[str]
    version: str
    size: str


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


def fromisoformat(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
