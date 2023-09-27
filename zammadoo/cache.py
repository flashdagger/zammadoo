#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from collections import OrderedDict
from itertools import islice
from typing import Any, Callable


class LruCache:
    def __init__(self, max_size=-1):
        self._cache = OrderedDict()
        self._max_size = max_size

    @property
    def max_size(self):
        return self._max_size

    @max_size.setter
    def max_size(self, value: int):
        self._max_size = value
        self.evict()

    def evict(self):
        max_size = self._max_size
        if max_size <= 0:
            return
        cache = self._cache
        evict_keys = tuple(islice(cache.keys(), max(0, len(cache) - max_size)))
        for key in evict_keys:
            del cache[key]

    def setdefault_by_callback(self, item, callback: Callable[[], Any]):
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

    def __contains__(self, item):
        return item in self._cache

    def __getitem__(self, item):
        cache = self._cache
        if self._max_size > 1:
            cache.move_to_end(item)
        return cache[item]

    def __setitem__(self, item, value):
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
