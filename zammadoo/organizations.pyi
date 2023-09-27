from .resource import Resource as Resource
from .resources import SearchableT
from .users import User

class Organization(Resource):
    created_by: User
    updated_by: User

class Organizations(SearchableT[Organization]):
    RESOURCE_TYPE = Organization
