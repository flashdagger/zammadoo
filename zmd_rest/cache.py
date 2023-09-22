from collections import OrderedDict
from itertools import islice
from typing import Callable, Any


class LruCache:
    def __init__(self, max_size=-1):
        self._cache = OrderedDict()
        self.max_size = max_size

    def evict(self):
        max_size = self.max_size
        if max_size <= 0:
            return
        cache = self._cache
        evict_keys = tuple(islice(cache.keys(), max(0, len(cache) - max_size)))
        for key in evict_keys:
            del cache[key]

    def setdefault_by_callback(self, item, callback: Callable[[], Any]):
        cache = self._cache
        if item in cache:
            cache.move_to_end(item)
            return cache[item]

        value = cache[item] = callback()
        max_size = self.max_size
        if 0 <= max_size < len(cache):
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
        cache.move_to_end(item)
        return cache[item]

    def __setitem__(self, item, value):
        cache = self._cache
        if item in cache:
            cache.move_to_end(item)
            cache[item] = value
        else:
            cache[item] = value
            max_size = self.max_size
            if 0 <= max_size < len(cache):
                cache.popitem(last=False)
