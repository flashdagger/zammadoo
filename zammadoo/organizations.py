from .resource import Resource
from .resources import SearchableG
from .users import UserProperty


class Organization(Resource):
    created_by = UserProperty()
    updated_by = UserProperty()


class Organizations(SearchableG[Organization]):
    RESOURCE_TYPE = Organization
