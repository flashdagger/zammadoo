#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import weakref
from dataclasses import asdict
from functools import partial
from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    Iterator,
    Literal,
    Optional,
    Type,
    TypedDict,
    TypeVar,
    cast,
)

from .cache import LruCache
from .utils import YieldCounter

if TYPE_CHECKING:
    from .client import Client

    # noinspection PyUnresolvedReferences
    from .resource import Resource
    from .utils import JsonDict, JsonDictList


_T_co = TypeVar("_T_co", bound="Resource", covariant=True)


class ParamDict(TypedDict):
    page: int
    per_page: int


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
        self._client = weakref.ref(client)
        self.endpoint: str = endpoint
        self.url = f"{client.url}/{endpoint}"  #: the resource's API URL

        self.cache = LruCache["JsonDict"](
            max_size=self.DEFAULT_CACHE_SIZE
        )  #: resource LRU cache

    def __call__(self, rid: int, *, info: Optional["JsonDict"] = None) -> _T_co:
        if info:
            assert (
                info.get("id") == rid
            ), "parameter info must contain 'id' and be equal with rid"
            self.cache[f"{self.url}/{rid}"] = info

        return self._RESOURCE_TYPE(self, rid, info=info)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.url!r}>"

    @property
    def client(self) -> "Client":
        client = self._client()
        assert client is not None, "missing client reference"
        return client

    def cached_info(self, rid: int, refresh=True, expand=False) -> "JsonDict":
        item = f"{self.url}/{rid}"
        cache = self.cache
        callback: Callable[[], "JsonDict"] = partial(
            self.client.get, self.endpoint, rid, params={"expand": expand or None}
        )

        if refresh:
            response = cache[item] = callback()
            return response

        return cache.setdefault_by_callback(item, callback)

    def delete(self, rid: int) -> None:
        """:meta private:"""
        item = f"{self.url}/{rid}"
        cache = self.cache
        self.client.delete(self.endpoint, rid)
        if item in cache:
            del cache[item]


class CreatableT(ResourcesT[_T_co]):
    def _create(self, json: "JsonDict") -> _T_co:
        created_info = self.client.post(self.endpoint, json=json)
        return self(created_info["id"], info=created_info)


class IterableT(ResourcesT[_T_co]):
    def _iter_items(self, items: "JsonDictList") -> Iterator[_T_co]:
        for item in items:
            rid = item["id"]
            assert isinstance(rid, int)
            self.cache[f"{self.url}/{rid}"] = item
            yield self._RESOURCE_TYPE(self, rid, info=item)

    def iter(self, *args, **params) -> Iterator[_T_co]:
        """
        .. py:module:: zammadoo.client
            :noindex:

        Iterate through all objects.

        With ``params`` you can also override the pagination defaults set in
        :attr:`Client.pagination`

        The returned iterable can be used in for loops
        or fill a Python container like :class:`list` or :class:`tuple`.

        ::

            items = tuple(resource.iter(...))

            for item in resource.iter(page=5, page_size=20, expand=True):
                print(item)

        :param args: additional endpoint arguments
        :param params: additional pagination options like ``page``, ``page_size``, ``extend``
        """
        # preserve the kwargs order
        if not params.get("page"):
            params["page"] = 1
        params.update(
            (
                (key, value)
                for key, value in asdict(self.client.pagination).items()
                if key not in params
            )
        )
        typed_params = cast(ParamDict, params)
        per_page = typed_params["per_page"]

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
        **params,
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
        :param params: additional pagination options like ``page``, ``page_size``, ``extend``
        """
        yield from self.iter(
            "search", query=query, sort_by=sort_by, order_by=order_by, **params
        )
