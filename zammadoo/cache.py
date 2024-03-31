#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from collections import OrderedDict
from collections.abc import Hashable
from datetime import datetime, timezone
from typing import Generic, Optional, Tuple, TypeVar

_T = TypeVar("_T")


class LruCache(Generic[_T]):
    def __init__(self, max_size=-1) -> None:
        self._cache: "OrderedDict[Hashable, Tuple[datetime, _T]]" = OrderedDict()
        self._max_size = max_size

    @property
    def max_size(self):
        return self._max_size

    @max_size.setter
    def max_size(self, value: int):
        self._max_size = value
        if value == 0:
            self._cache.clear()
        elif value > 0:
            self.evict()

    def evict(self) -> None:
        max_size = self._max_size
        if max_size <= 0:
            return

        cache = self._cache
        for _ in range(len(cache) - max_size):
            cache.popitem(last=False)

    def setdefault(self, item, default: _T) -> _T:
        max_size = self._max_size
        if max_size == 0:
            return default

        cache = self._cache
        if item in cache:
            if max_size > 1:
                cache.move_to_end(item)
            return cache[item][1]

        cache[item] = datetime.now(timezone.utc), default
        if 0 < max_size < len(cache):
            cache.popitem(last=False)

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
        if self._max_size > 1:
            cache.move_to_end(item)
        return cache[item][1]

    def __setitem__(self, item: Hashable, value: _T) -> None:
        max_size = self._max_size
        if max_size == 0:
            return

        cache = self._cache
        timestamp = datetime.now(timezone.utc)
        if item in cache:
            if max_size > 1:
                cache.move_to_end(item)
            cache[item] = timestamp, value
        else:
            cache[item] = timestamp, value
            if 0 < max_size < len(cache):
                cache.popitem(last=False)

    def __delitem__(self, item: Hashable) -> None:
        del self._cache[item]

    def timestamp(self, item: Hashable) -> Optional[datetime]:
        data = self._cache.get(item)
        return data and data[0]
