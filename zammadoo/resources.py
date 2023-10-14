#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from dataclasses import asdict
from functools import partial
from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    Iterator,
    Literal,
    MutableMapping,
    Optional,
    Type,
    TypeVar,
)
from weakref import WeakValueDictionary

from .cache import LruCache
from .utils import YieldCounter, info_cast

if TYPE_CHECKING:
    from .client import Client
    from .resource import Resource
    from .utils import JsonDict, JsonDictList

    _ = Resource

_T_co = TypeVar("_T_co", bound="Resource", covariant=True)


class ResourcesT(Generic[_T_co]):
    _RESOURCE_TYPE: Type[_T_co]
    DEFAULT_CACHE_SIZE = -1
    """
    controls the LRU cache behaviour

        * LRU disabled, cache unbounded (-1)
        * disable caching (0)
        * limited LRU caching (>0)
    """

    def __init__(self, client: "Client", endpoint: str):
        self.client = client
        self.endpoint: str = endpoint
        self.cache = LruCache["JsonDict"](
            max_size=self.DEFAULT_CACHE_SIZE
        )  #: resource LRU cache
        self._instance_cache: MutableMapping[int, _T_co] = WeakValueDictionary()

    def __call__(self, rid: int, *, info: Optional["JsonDict"] = None) -> _T_co:
        if info:
            assert (
                info.get("id") == rid
            ), "parameter info must contain 'id' and be equal with rid"
            self.cache[f"{self.url}/{rid}"] = info

        instance_map = self._instance_cache
        instance = instance_map.get(rid)
        if not instance or info:
            instance = instance_map[rid] = self._RESOURCE_TYPE(self, rid, info=info)
        return instance

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.url!r}>"

    @property
    def url(self) -> str:
        """the resource's API URL"""
        return f"{self.client.url}/{self.endpoint}"

    def cached_info(self, rid: int, refresh=True) -> "JsonDict":
        item = f"{self.url}/{rid}"
        cache = self.cache
        callback: Callable[[], "JsonDict"] = partial(
            self.client.get, self.endpoint, rid
        )

        if not refresh:
            return cache.setdefault_by_callback(item, callback)

        response = callback()
        cache[item] = response
        return response


class CreatableT(ResourcesT[_T_co]):
    def _create(self, json: "JsonDict") -> _T_co:
        created_info = self.client.post(self.endpoint, json=json)
        return self(created_info["id"], info=created_info)


class IterableT(ResourcesT[_T_co]):
    def _iter_items(self, items: "JsonDictList") -> Iterator[_T_co]:
        for item in items:
            rid = info_cast(item)["id"]
            self.cache[f"{self.url}/{rid}"] = item
            yield self._RESOURCE_TYPE(self, rid, info=item)

    def iter(self, *args, **params) -> Iterator[_T_co]:
        """
        Iterate through all objects. The returned iterable can be used in for loops
        or fill a Python container like :class:`list` or :class:`tuple`.

        ::

            items = tuple(resource.iter(...))

            for item in resource.iter(...):
                print(item)

        :param args: additional endpoint arguments
        :param params: additional pagination options like ``page``, ``page_size``, ``extend``
        """
        # preserve the kwargs order
        params.update(
            (
                (key, value)
                for key, value in asdict(self.client.pagination).items()
                if key not in params
            )
        )
        typed_params = info_cast(params)
        per_page = typed_params["per_page"]
        if typed_params["page"] is None:
            typed_params["page"] = 1

        while True:
            items = self.client.get(self.endpoint, *args, params=params)
            counter = YieldCounter()

            yield from counter(self._iter_items(items))
            yielded = counter.yielded

            if per_page and yielded < per_page or yielded == 0:
                return

            typed_params["page"] += 1

    def __iter__(self) -> Iterator[_T_co]:
        return self.iter()


class SearchableT(IterableT[_T_co]):
    def search(
        self,
        query: str,
        *,
        sort_by: Optional[str] = None,
        order_by: Literal["asc", "desc", None] = None,
        **kwargs,
    ) -> Iterator[_T_co]:
        """
        Search for objects with
        `query syntax <https://user-docs.zammad.org/en/latest/advanced/search.html>`_.

        The returned iterable can be used in for loops
        or fill a Python container like :class:`list` or :class:`tuple`.

        ::

            items = tuple(resource.search(...))

            for item in resource.search(...):
                print(item)



        :param query: query string
        :param sort_by: sort by a specific property (e.g. ``name``)
        :param order_by: sort direction
        :param kwargs: additional pagination options like ``page``, ``page_size``, ``extend``
        """
        yield from self.iter(
            "search", query=query, sort_by=sort_by, order_by=order_by, **kwargs
        )
