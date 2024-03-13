#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from contextlib import suppress
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
    TypedDict,
    TypeVar,
    Union,
    cast,
    get_args,
)

if TYPE_CHECKING:
    from os import PathLike

    from typing_extensions import TypeAlias

    LinkType: TypeAlias = Literal["normal", "parent", "child"]
    _ = PathLike
else:
    LinkType = Literal["normal", "parent", "child"]

LINK_TYPES = get_args(LinkType)

JsonType = Union[None, bool, int, float, str, List["JsonType"], "JsonDict"]
JsonDict = Dict[str, JsonType]
JsonDictList = List[JsonDict]
JsonContainer = Union[JsonDict, JsonDictList]
StringKeyMapping = Mapping[str, Any]
PathType = Union[str, "PathLike[Any]"]


class TypedTag(TypedDict):
    id: int
    name: str
    count: Optional[int]


class TypedInfo(TypedDict, total=False):
    article_ids: List[int]
    create_article_sender: str
    create_article_type: str
    id: int
    page: int
    parent_id: Optional[int]
    per_page: int
    permissions: List[str]
    preferences: Dict[str, str]
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


class FrozenInfo:
    def __init__(
        self,
        info: Optional["JsonDict"] = None,
    ) -> None:
        self._info: "JsonDict" = info or {}
        self._frozen = True

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

    def _initialize(self) -> None:
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
        self._initialize()
        return self._info[name]

    def __dir__(self):
        names = super().__dir__()
        extra_attributes = set(self._info.keys()) - set(names)
        return chain(names, extra_attributes)

    def view(self) -> "MappingProxyType[str, JsonType]":
        """
        A mapping view of the objects internal properties as returned by the REST API.

        :rtype: :class:`MappingProxyType[str, Any]`
        """
        self._initialize()
        return MappingProxyType(self._info)
