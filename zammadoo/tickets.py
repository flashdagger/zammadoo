from datetime import datetime
from typing import Iterable

from .resource import Resource, ResourceGetter, ResourceListGetter
from .resources import SearchableG
from .utils import JsonContainer

Article = Resource
Group = Resource
Organization = Resource
Priority = Resource
State = Resource
User = Resource


class Ticket(Resource):
    articles = ResourceListGetter[Article]("ticket_articles")
    created_at: datetime
    created_by = ResourceGetter[User]("users")
    customer = ResourceGetter[User]("users")
    group = ResourceGetter[Group]()
    note: str
    number: str
    organization = ResourceGetter[Organization]()
    owner = ResourceGetter[User]("users")
    priority = ResourceGetter[Priority]("ticket_priorities")
    state = ResourceGetter[State]("ticket_states")
    title: str
    updated_by = ResourceGetter[User]("users")


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
