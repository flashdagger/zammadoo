from collections.abc import Mapping as MappingABC
from types import MappingProxyType
from typing import Callable, Dict, Mapping


class LazyMapping(MappingABC):
    """mapping type which is lazily updated by a callable"""

    def __init__(self, func: Callable[[], Mapping]):
        self._dict: Dict = {}
        self._updater = func
        self._needs_update = True

    def update(self):
        self._dict.update(self._updater())
        self._needs_update = False

    def view(self) -> MappingProxyType:
        if self._needs_update:
            self.update()
        return MappingProxyType(self._dict)

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self._updater})"

    def __len__(self):
        if self._needs_update:
            self.update()
        return len(self._dict)

    def __getitem__(self, item):
        if self._needs_update:
            self.update()
        return self._dict[item]

    def __iter__(self):
        if self._needs_update:
            self.update()
        return iter(self._dict)
