#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from collections import OrderedDict
from collections.abc import Hashable
from time import monotonic
from typing import Generic, Optional, Tuple, TypeVar

_T = TypeVar("_T")


class LruCache(Generic[_T]):
    def __init__(self, max_size: int = -1) -> None:
        self._cache: "OrderedDict[Hashable, Tuple[float, _T]]" = OrderedDict()
        self._max_size = max_size

    @property
    def max_size(self) -> int:
        return self._max_size

    @max_size.setter
    def max_size(self, value: int):
        self._max_size = max(value, -1)
        self.evict()

    def evict(self) -> None:
        max_size = self._max_size
        if max_size < 0:
            return

        cache = self._cache
        if max_size == 0:
            cache.clear()
            return

        for _ in range(len(cache) - max_size):
            cache.popitem(last=False)

    def setdefault(self, item, default: _T) -> _T:
        max_size = self._max_size
        if max_size == 0:
            return default

        cache = self._cache
        if item in cache:
            cache.move_to_end(item)
            return cache[item][1]

        if 0 < max_size <= len(cache):
            cache.popitem(last=False)

        cache[item] = monotonic(), default
        return default

    def clear(self) -> None:
        self._cache.clear()

    def keys(self):
        return self._cache.keys()

    def values(self):
        return (value for _, value in self._cache.values())

    def items(self):
        return ((key, value) for key, (_, value) in self._cache.items())

    def __len__(self):
        return len(self._cache)

    def __contains__(self, item: Hashable):
        return item in self._cache

    def __getitem__(self, item: Hashable) -> _T:
        cache = self._cache
        cache.move_to_end(item)
        return cache[item][1]

    def __setitem__(self, item: Hashable, value: _T) -> None:
        max_size = self._max_size
        if max_size == 0:
            return

        cache = self._cache
        if item in cache:
            cache.move_to_end(item)
        elif 0 < max_size <= len(cache):
            cache.popitem(last=False)

        cache[item] = monotonic(), value

    def __delitem__(self, item: Hashable) -> None:
        del self._cache[item]

    def age_s(self, item: Hashable) -> Optional[float]:
        try:
            return monotonic() - self._cache[item][0]
        except KeyError:
            return None
