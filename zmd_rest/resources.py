import json
from typing import (
    Union,
    Dict,
    Generic,
    Type,
    TypeVar,
    Iterable,
    TYPE_CHECKING,
)

from .resource import Rid, Resource
from .utils import join, JsonDict, JsonContainer, JsonMapping

if TYPE_CHECKING:
    from . import Client


T = TypeVar("T")


class ResourcesABC(Generic[T]):
    RESOURCE_TYPE: Type[T]


class Resources(ResourcesABC[Resource]):
    RESOURCE_TYPE = Resource
    CACHE: Dict[str, "Resources"] = {}

    class UnsupportedEndpoint(Exception):
        pass

    def __new__(cls, client: "Client", endpoint: str):
        url = join(client.url, endpoint)
        cache = cls.CACHE
        if url not in cache:
            obj = cache[url] = super().__new__(cls)
            return obj
        return cache[url]

    def __init__(self, client: "Client", endpoint: str):
        if endpoint not in client.__ano__:
            raise Resources.UnsupportedEndpoint(endpoint)
        self.client = client
        self.endpoint = endpoint

    def __call__(self, rid: Rid) -> Resource:
        return self.RESOURCE_TYPE(self, rid)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.url!r}>"

    def __iter__(self):
        return self.iter()

    @property
    def url(self):
        return join(self.client.url, self.endpoint)

    def as_endpoint(self, endpoint: str):
        return self.__class__(self.client, endpoint)

    def get(self, rid: Union[int, str]) -> JsonContainer:
        return self.client.get(self.endpoint, rid)

    def create(self, params: JsonMapping) -> JsonDict:
        return self.client.create(params=params)

    def update(self, rid: int, params: JsonMapping) -> JsonDict:
        return self.client.update(self.endpoint, rid, params=params)

    def delete(self, rid: int) -> JsonDict:
        return self.client.delete(self.endpoint, rid)

    def _pagination(self, *args, **params) -> Iterable[Resource]:
        while True:
            items = self.client.get(self.endpoint, *args, params=params)

            if isinstance(items, dict):
                with open("dump.json", "w", encoding="utf8") as fd:
                    json.dump(items, fd, indent=2)

                _mapping, items = items, list(
                    items["assets"].get(self.endpoint[:-1].capitalize(), {}).values()
                )

            assert isinstance(items, list), f"expected a list, got {type(items)}"
            for item in items:
                yield self.RESOURCE_TYPE(self, -1, info=item)

            if len(items) < params["per_page"]:
                return

            params["page"] += 1

    def iter(self, *, page=1, per_page=10, expand=False) -> Iterable[Resource]:
        params = {"page": page, "per_page": per_page, "expand": expand}
        return self._pagination(**params)

    def search(
        self, query: str, *, page=1, per_page=10, expand=False, **kwargs
    ) -> Iterable[Resource]:
        params = {"query": query, "page": page, "per_page": per_page, "expand": expand}
        params.update(kwargs)
        return self._pagination("search", **params)
