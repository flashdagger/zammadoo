#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import Any, Dict, List, Union

JsonType = Union[None, bool, int, float, str, List["JsonType"], "JsonDict"]
JsonDict = Dict[str, JsonType]
JsonDictList = List[JsonDict]
JsonContainer = Union[JsonDict, JsonDictList]
StringKeyDict = Dict[str, Any]
