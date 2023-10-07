#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import Iterable, Literal, TypeVar, get_args

_T = TypeVar("_T")
LINK_TYPE = Literal["normal", "parent", "child"]  # pylint: disable=invalid-name
LINK_TYPES = get_args(LINK_TYPE)


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
