#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import Any, Dict, Iterable, List, TypeVar, Union

_T = TypeVar("_T")


class YieldCounter:
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


JsonType = Union[None, bool, int, float, str, List["JsonType"], Dict[str, "JsonType"]]
JsonDict = Dict[str, JsonType]
JsonDictList = List[JsonDict]
JsonContainer = Union[JsonDict, JsonDictList]
StringKeyDict = Dict[str, Any]
