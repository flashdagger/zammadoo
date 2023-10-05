#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from copy import copy
from dataclasses import asdict
from functools import partial
from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    Iterable,
    Literal,
    MutableMapping,
    Optional,
    Type,
    TypeVar,
)
from weakref import WeakValueDictionary

from .cache import LruCache
from .resource import Resource
from .utils import JsonContainer, JsonDict, YieldCounter

if TYPE_CHECKING:
    from .client import Client

_T_co = TypeVar("_T_co", bound=Resource, covariant=True)


class ResourcesT(Generic[_T_co]):
    RESOURCE_TYPE: Type[_T_co]
    DEFAULT_CACHE_SIZE = -1

    def __init__(self, client: "Client", endpoint: str):
        self.client = client
        self.endpoint: str = endpoint
        self.cache = LruCache[JsonContainer](max_size=self.DEFAULT_CACHE_SIZE)
        self._instance_cache: MutableMapping[int, _T_co] = WeakValueDictionary()

    def __call__(self, rid: int, *, info: Optional[JsonDict] = None) -> _T_co:
        if info:
            assert (
                info.get("id") == rid
            ), "parameter info must contain 'id' and be equal with rid"
            self.cache[self.url(rid)] = info

        instance_map = self._instance_cache
        instance = instance_map.get(rid)
        if not instance or info:
            instance = instance_map[rid] = self.RESOURCE_TYPE(self, rid, info=info)
        return instance

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.url()!r}>"

    def url(self, *args) -> str:
        return "/".join(map(str, (self.client.url, self.endpoint, *args)))

    def cached_info(self, rid: int, refresh=True) -> JsonContainer:
        item = self.url(rid)
        cache = self.cache
        callback: Callable[[], JsonContainer] = partial(
            self.client.get, self.endpoint, rid
        )

        if not refresh:
            return cache.setdefault_by_callback(item, callback)

        response = callback()
        cache[item] = response
        return response


class Creatable(ResourcesT[_T_co]):
    def _create_with_name(self, name, **kwargs):
        return self._create({"name": name, **kwargs})

    def _create(self, json: JsonDict) -> _T_co:
        created_info = self.client.post(self.endpoint, json=json)
        return self(created_info["id"], info=created_info)


class IterableT(ResourcesT[_T_co]):
    def __init__(self, client: "Client", endpoint: str):
        super().__init__(client, endpoint)
        self.pagination = copy(client.pagination)

    def _iter_items(self, items: JsonContainer) -> Iterable[_T_co]:
        assert isinstance(items, list)
        for item in items:
            yield self.RESOURCE_TYPE(self, item["id"], info=item)  # type: ignore[arg-type]

    def iter(self, *args, **params) -> Iterable[_T_co]:
        # preserve the kwargs order
        params.update(
            (
                (key, value)
                for key, value in asdict(self.pagination).items()
                if key not in params
            )
        )
        per_page = params["per_page"]
        if params["page"] is None:
            params["page"] = 1
        assert params["page"] is not None  # make mypy happy

        while True:
            items = self.client.get(self.endpoint, *args, params=params)
            counter = YieldCounter()

            yield from counter(self._iter_items(items))
            yielded = counter.yielded

            if per_page and yielded < per_page or yielded == 0:
                return

            params["page"] += 1

    def __iter__(self):
        return self.iter()


class SearchableT(IterableT[_T_co]):
    def search(
        self,
        query: str,
        *,
        sort_by: Optional[str] = None,
        order_by: Literal["asc", "desc", None] = None,
        **kwargs,
    ) -> Iterable[_T_co]:
        yield from self.iter(
            "search", query=query, sort_by=sort_by, order_by=order_by, **kwargs
        )
