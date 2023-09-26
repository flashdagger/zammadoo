from typing import Any, Dict, Iterable, List, Mapping, Union


class YieldCounter:
    def __init__(self):
        self._counter = 0

    @property
    def yielded(self):
        return self._counter

    def iter(self, itr: Iterable) -> Iterable:
        for item in itr:
            yield item
            self._counter += 1


def join(*args) -> str:
    return "/".join(map(str, args))


JsonType = Union[int, bool, None, float, str, "JsonList", "JsonDict"]
JsonDict = Dict[str, Any]
JsonList = List[JsonDict]
JsonContainer = Union[JsonDict, JsonList]
JsonMapping = Mapping[str, Any]
