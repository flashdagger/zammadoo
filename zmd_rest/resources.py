from copy import copy
from dataclasses import asdict
from functools import partial
from typing import TYPE_CHECKING, Generic, Iterable, Optional, Type, TypeVar

from .cache import LruCache
from .resource import Resource
from .utils import JsonContainer

if TYPE_CHECKING:
    from . import Client


T = TypeVar("T", bound=Resource)


class ResourcesG(Generic[T]):
    RESOURCE_TYPE: Type[T]
    CACHE_SIZE = 10

    def __init__(self, client: "Client", endpoint: str):
        self.client = client
        self.endpoint = endpoint
        self.cache = LruCache(max_size=self.CACHE_SIZE)
        self._url = f"{client.url}/{endpoint}"

    def __call__(self, rid: int) -> T:
        return self.RESOURCE_TYPE(self, rid)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.url()!r}>"

    def url(self, rid: Optional[int] = None):
        url = self._url
        if rid is None:
            return url
        return f"{url}/{rid}"

    def get(self, rid: int, refresh=True) -> JsonContainer:
        item = self.url(rid)
        cache = self.cache
        callback = partial(self.client.get, self.endpoint, rid)

        if not refresh:
            return cache.setdefault_by_callback(item, callback)

        response = callback()
        cache[item] = response
        return response


class IterableResourcesG(ResourcesG[T]):
    def __init__(self, client: "Client", endpoint: str):
        super().__init__(client, endpoint)
        self.pagination = copy(client.pagination)

    def _iter_items(self, items: JsonContainer) -> Iterable[T]:
        assert isinstance(items, list)
        for item in items:
            rid = item["id"]
            self.cache[self.url(rid)] = item
            yield self.RESOURCE_TYPE(self, rid)

    def iter(self, *args, **kwargs) -> Iterable[T]:
        params = asdict(self.pagination)
        params.update(kwargs)
        kwargs.update(params)  # preserves the kwargs order
        while True:
            items = self.client.get(self.endpoint, *args, params=kwargs)
            yield from self._iter_items(items)

            if len(items) < params["per_page"]:
                return

            params["page"] += 1

    __iter__ = iter


class SearchableG(IterableResourcesG[T]):
    def search(
        self,
        query: str,
        sort_by: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Iterable[T]:
        return self.iter(
            "search", query=query, sort_by=sort_by, limit=limit, order_by=order_by
        )


class Resources(ResourcesG[Resource]):
    RESOURCE_TYPE = Resource


class Searchable(SearchableG[Resource]):
    RESOURCE_TYPE = Resource
