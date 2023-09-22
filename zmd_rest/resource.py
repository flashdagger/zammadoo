from contextlib import suppress
from datetime import datetime
from types import MappingProxyType
from typing import Union, Optional, Dict, Any, Mapping, cast, TYPE_CHECKING

from .lazymapping import LazyMapping
from .utils import join

if TYPE_CHECKING:
    from .resources import Resources

Rid = Union[str, int]


class Resource:
    def __init__(
        self, resources: "Resources", rid: Rid, info: Optional[Dict[str, Any]] = None
    ):
        self._resources = resources
        if info is None:
            self._id = rid
            self._info: Mapping[str, Any] = LazyMapping(
                lambda: cast(Mapping, self._resources.get(rid))
            )
        else:
            self._id = info["id"]
            self._info = info

    def __repr__(self):
        url = join(self._resources.url, self.id)
        return f"<{self.__class__.__qualname__} {url!r}>"

    def __getattr__(self, item: str):
        try:
            value = self._info[item]
            if isinstance(value, str):
                with suppress(ValueError):
                    return datetime.fromisoformat(value)
            return value
        except KeyError as _exc:
            value = self._info.get(f"{item}_id")
            endpoint = f"{item}s"
            if isinstance(value, int) and endpoint in self._resources.client.__ano__:
                return self._resources.as_endpoint(endpoint)(value)

            if item in self._resources.client.__ano__:
                assert item.endswith("s"), f"{item} is not a plural"
                values = self._info.get(f"{item[:-1]}_ids")
                assert isinstance(values, list) and all(
                    isinstance(value, int) for value in values
                ), (item, values)
                return [self._resources.as_endpoint(item)(value) for value in values]

            if item.endswith("_by"):
                value = self._info.get(f"{item}_id")
                if isinstance(value, int):
                    return self._resources.as_endpoint("users")(value)

        raise AttributeError(
            f"{self.__class__.__name__!r} object has no attribute {item!r}"
        )

    def __getitem__(self, item: str):
        return self._info[item]

    @property
    def id(self):
        return self._id

    @property
    def info(self) -> MappingProxyType[str, Any]:
        info = self._info
        if isinstance(info, LazyMapping):
            return info.view()
        return MappingProxyType(self._info)

    def reload(self):
        info = self._info
        if isinstance(info, LazyMapping):
            info.update()
        else:
            info.clear()
            info.update(self._resources.get(self._id))
