from contextlib import suppress
from datetime import datetime
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Generic, Type, Optional, TypeVar

from .utils import JsonDict

if TYPE_CHECKING:
    from .resources import ResourcesG, Resources


class Resource:
    def __init__(self, resources: "ResourcesG", rid: int):
        self._id = rid
        self._resources = resources
        self._info: JsonDict = {}

    def __repr__(self):
        url = self._resources.url(self.id)
        return f"<{self.__class__.__qualname__} {url!r}>"

    def __getattr__(self, item: str):
        try:
            value = self[item]
        except KeyError as exc:
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no attribute {item!r}"
            ) from exc

        if isinstance(value, str):
            with suppress(ValueError):
                return datetime.fromisoformat(value)
        return value

    def __getitem__(self, item: str):
        self._initialize()
        return self._info[item]

    @property
    def id(self):
        return self._id

    @property
    def info(self) -> MappingProxyType[str, Any]:
        self._initialize()
        return MappingProxyType(self._info)

    def _initialize(self):
        if self._info:
            return
        self._info.update(self._resources.get(self._id, refresh=False))

    def reload(self):
        info = self._info
        info.clear()
        info.update(self._resources.get(self._id), refresh=True)


T = TypeVar("T", bound=Resource)


class ResourceGetter(Generic[T]):
    def __init__(self, endpoint="", key=""):
        self.endpoint = endpoint
        self.key = key

    def __set_name__(self, owner, name):
        self.key = f"{name}_id"
        if not self.endpoint:
            self.endpoint = f"{name}s"

    def __get__(self, instance: Resource, owner: Type[Resource]) -> Optional[T]:
        rid = instance[self.key]
        resources: Resources = getattr(instance, "_resources")
        return rid and getattr(resources.client, self.endpoint)(rid)
