from typing import cast

from .resource import Resource, ResourceGetter
from .resources import IterableG
from .users import User


class State(Resource):
    created_by = cast(User, ResourceGetter("users"))
    updated_by = cast(User, ResourceGetter("users"))


class States(IterableG[State]):
    RESOURCE_TYPE = State
