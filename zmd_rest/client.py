import atexit
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Type,
)

import requests
from requests import HTTPError

from .resources import Resources
from .utils import join, JsonDict, JsonContainer, JsonMapping


def raise_or_return_json(response: requests.Response) -> JsonContainer:
    try:
        response.raise_for_status()
    except HTTPError as exc:
        raise HTTPError(response.text) from exc

    return response.json()


class ClientMeta(type):
    def __init__(cls, name, bases, attributes):
        super().__init__(name, bases, attributes)
        mapping = getattr(cls, "__ano__")
        for base_cls in reversed(cls.mro()):
            ano = base_cls.__dict__.get("__annotations__", {})
            mapping.update(
                (key, value)
                for key, value in ano.items()
                if isinstance(value, type) and issubclass(value, Resources)
            )


class Client(metaclass=ClientMeta):
    groups: Resources
    links: Resources
    object_manager_attributes: Resources
    online_notifications: Resources
    organizations: Resources
    roles: Resources
    # tags: Resources
    tag_list: Resources
    ticket_article_plain: Resources
    ticket_articles: Resources
    ticket_attachment: Resources
    ticket_priorities: Resources
    ticket_states: Resources
    tickets: Resources
    users: Resources

    __ano__: Dict[str, Type[Resources]] = {}

    class ConfigException(Exception):
        pass

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        http_token: Optional[str] = None,
        oauth2_token: Optional[str] = None,
        # on_behalf_of: Optional[str] = None,
        additional_headers: Optional[List[Tuple[str, str]]] = None,
    ) -> None:
        self.url = url.rstrip("/")
        self._username = username
        self._password = password
        self._http_token = http_token
        self._oauth2_token = oauth2_token
        # self._on_behalf_of = on_behalf_of
        self._additional_headers = additional_headers
        self._check_config()

        self.session = requests.Session()
        atexit.register(self.session.close)
        self.session.headers["User-Agent"] = "Zammad API Python"
        if self._http_token:
            self.session.headers["Authorization"] = f"Token token={self._http_token}"
        elif oauth2_token:
            self.session.headers["Authorization"] = f"Bearer {self._oauth2_token}"
        elif self._username and self._password:  # noqa: SIM106
            self.session.auth = (self._username, self._password)
        else:
            raise ValueError("Invalid Authentication information in config")

        # if self._on_behalf_of:
        #     self.session.headers["X-On-Behalf-Of"] = self._on_behalf_of

        if self._additional_headers:
            for additional_header in self._additional_headers:
                self.session.headers[additional_header[0]] = additional_header[1]

    def _check_config(self) -> None:
        """Check the configuration"""
        if not self.url:
            raise Client.ConfigException("Missing url in config")
        if self._http_token:
            return
        if self._oauth2_token:
            return
        if not self._username:
            raise Client.ConfigException("Missing username in config")
        if not self._password:
            raise Client.ConfigException("Missing password in config")

    def __getattr__(self, item) -> Resources:
        klass = self.__ano__.get(item)
        if not klass:
            raise AttributeError(item)
        return klass(self, item)

    def get(self, *args, params: Optional[JsonMapping] = None) -> JsonContainer:
        print("--> get", args)
        response = self.session.get(join(self.url, *args), params=params)
        return raise_or_return_json(response)

    def create(self, *args, params: JsonMapping) -> JsonDict:
        response = self.session.post(join(self.url, *args), json=params)
        value = raise_or_return_json(response)
        assert isinstance(value, dict)
        return value

    def update(self, *args, params: JsonMapping) -> JsonDict:
        response = self.session.put(join(self.url, *args), json=params)
        value = raise_or_return_json(response)
        assert isinstance(value, dict)
        return value

    def delete(self, *args) -> JsonDict:
        response = self.session.get(join(self.url, *args))
        value = raise_or_return_json(response)
        assert isinstance(value, dict)
        return value
