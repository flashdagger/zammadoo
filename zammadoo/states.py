from .resource import Resource, ResourceGetter
from .resources import IterableG

User = Resource


class State(Resource):
    created_by = ResourceGetter[User]("users")
    updated_by = ResourceGetter[User]("users")


class States(IterableG[State]):
    RESOURCE_TYPE = State
