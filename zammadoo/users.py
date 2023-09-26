from functools import partial
from typing import cast, TYPE_CHECKING

from .resource import Resource, ResourceGetter
from .resources import SearchableG

if TYPE_CHECKING:
    from .organizations import Organization


class User(Resource):
    created_by = cast("User", ResourceGetter("users"))
    organization = cast("Organization", ResourceGetter("organizations"))


class Users(SearchableG[User]):
    RESOURCE_TYPE = User

    # pylint: disable=invalid-name
    def me(self) -> User:
        cache = self.cache
        endpoint = "users/me"
        url = f"{self.url()}/{endpoint}"
        callback = partial(self.client.get, endpoint)

        info = cache.setdefault_by_callback(url, callback)
        uid = info["id"]
        cache[self.url(uid)] = info
        return self.RESOURCE_TYPE(self, uid)
