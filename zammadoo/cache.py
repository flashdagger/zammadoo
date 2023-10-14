#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from collections import OrderedDict
from itertools import islice
from typing import Callable, Generic, Hashable, TypeVar

_T = TypeVar("_T")


class LruCache(Generic[_T]):
    def __init__(self, max_size=-1) -> None:
        self._cache: "OrderedDict[Hashable, _T]" = OrderedDict()
        self._max_size = max_size

    @property
    def max_size(self):
        return self._max_size

    @max_size.setter
    def max_size(self, value: int):
        self._max_size = value
        self.evict()

    def evict(self) -> None:
        max_size = self._max_size
        if max_size <= 0:
            return
        cache = self._cache
        evict_keys = tuple(islice(cache.keys(), max(0, len(cache) - max_size)))
        for key in evict_keys:
            del cache[key]

    def setdefault_by_callback(self, item, callback: Callable[[], _T]) -> _T:
        max_size = self._max_size
        if max_size == 0:
            return callback()

        cache = self._cache
        if item in cache:
            if max_size > 1:
                cache.move_to_end(item)
            return cache[item]

        value = cache[item] = callback()
        if 0 < max_size < len(cache):
            cache.popitem(last=False)

        return value

    def clear(self):
        self._cache.clear()

    def keys(self):
        return self._cache.keys()

    def values(self):
        return self._cache.values()

    def items(self):
        return self._cache.items()

    def __len__(self):
        return len(self._cache)

    def __contains__(self, item: Hashable):
        return item in self._cache

    def __getitem__(self, item: Hashable) -> _T:
        cache = self._cache
        if self._max_size > 1:
            cache.move_to_end(item)
        return cache[item]

    def __setitem__(self, item: Hashable, value: _T) -> None:
        max_size = self._max_size
        if max_size == 0:
            return

        cache = self._cache
        if item in cache:
            if max_size > 1:
                cache.move_to_end(item)
            cache[item] = value
        else:
            cache[item] = value
            if 0 < max_size < len(cache):
                cache.popitem(last=False)

    def __delitem__(self, item: Hashable) -> None:
        del self._cache[item]
