from datetime import datetime
from typing import Iterable, Optional, cast

from .organizations import Organization
from .resource import Resource, ResourceGetter, ResourceListGetter
from .resources import SearchableG
from .states import State
from .users import User
from .utils import JsonContainer

Article = Resource
Group = Resource
Priority = Resource


class Ticket(Resource):
    articles = ResourceListGetter[Article]("ticket_articles")
    created_at: datetime
    created_by = cast(User, ResourceGetter("users"))
    customer = cast(User, ResourceGetter("users"))
    group = cast(Group, ResourceGetter())
    note: str
    number: str
    organization = cast(Organization, ResourceGetter())
    owner = cast(User, ResourceGetter("users"))
    priority = cast(Priority, ResourceGetter("ticket_priorities"))
    state = cast(State, ResourceGetter("ticket_states"))
    title: str
    updated_by = cast(Optional[User], cast(User, ResourceGetter("users")))


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
