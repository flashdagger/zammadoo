#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import Any, Dict, Iterable, List, Mapping, Union


class YieldCounter:
    def __init__(self):
        self._counter = 0

    @property
    def yielded(self):
        return self._counter

    def __call__(self, itr: Iterable) -> Iterable:
        self._counter = 0
        for count, item in enumerate(itr, 1):
            self._counter = count
            yield item


def join(*args) -> str:
    return "/".join(map(str, args))


JsonType = Union[int, bool, None, float, str, "JsonList", "JsonDict"]
JsonDict = Dict[str, Any]
JsonList = List[JsonDict]
JsonContainer = Union[JsonDict, JsonList]
JsonMapping = Mapping[str, Any]
