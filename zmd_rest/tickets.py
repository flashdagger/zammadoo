from types import MethodType
from typing import Iterable, Optional, List

from .resource import Resource
from .resources import SearchableG
from .utils import JsonContainer

Article = Resource
Group = Resource
User = Resource
Organization = Resource


def decorator_factory(endpoint=""):
    def _decorator(method: MethodType):
        name = method.__name__
        id_spec = f"{name}_id"

        # pylint: disable=protected-access
        def _resource_getter(self):
            rid = self[id_spec]
            return rid and getattr(self._resources.client, endpoint or f"{name}s")(rid)

        return property(_resource_getter)

    return _decorator


resource_by_id = decorator_factory()
user_by_id = decorator_factory("users")


class Ticket(Resource):
    @resource_by_id
    def group(self) -> Optional[Group]:
        ...

    @user_by_id
    def owner(self) -> User:
        ...

    @resource_by_id
    def organization(self) -> Optional[Organization]:
        ...

    @user_by_id
    def customer(self) -> User:
        ...

    @user_by_id
    def created_by(self) -> User:
        ...

    @user_by_id
    def updated_by(self) -> Optional[User]:
        ...

    @property
    def articles(self) -> List[Article]:
        return [self._resources.client.ticket_articles(aid) for aid in self.article_ids]


class Tickets(SearchableG[Ticket]):
    RESOURCE_TYPE = Ticket

    def _iter_items(self, items: JsonContainer) -> Iterable[Ticket]:
        if isinstance(items, list):
            yield from super()._iter_items(items)
            return

        assert isinstance(items, dict)
        for key, asset in items.get("assets", {}).items():
            resources = getattr(self.client, f"{key.lower()}s")
            for rid_s, info in asset.items():
                url = resources.url(rid_s)
                resources.cache[url] = info

        for rid in items.get("tickets", ()):
            yield self.RESOURCE_TYPE(self, rid)
