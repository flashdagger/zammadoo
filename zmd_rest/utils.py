from typing import Union, Dict, List, Mapping, Any


def join(*args) -> str:
    return "/".join(map(str, args))


JsonType = Union[int, bool, None, float, str, "JsonList", "JsonDict"]
JsonDict = Dict[str, Any]
JsonList = List[JsonDict]
JsonContainer = Union[JsonDict, JsonList]
JsonMapping = Mapping[str, Any]
