from functools import partial
from typing import TYPE_CHECKING, cast

from .resource import Resource, ResourceProperty
from .resources import SearchableG

if TYPE_CHECKING:
    from .organizations import Organization

    _ = Organization


class UserProperty(ResourceProperty["User"]):
    def __init__(self, key=None):
        super().__init__(endpoint="users", key=key or "")


class User(Resource):
    created_by = UserProperty()
    organization = cast("Organization", ResourceProperty("organizations"))


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
