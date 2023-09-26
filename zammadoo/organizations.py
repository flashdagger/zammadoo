from typing import cast

from .resource import Resource, ResourceGetter
from .resources import SearchableG
from .users import User


class Organization(Resource):
    created_by = cast(User, ResourceGetter("users"))
    updated_by = cast(User, ResourceGetter("users"))


class Organizations(SearchableG[Organization]):
    RESOURCE_TYPE = Organization
