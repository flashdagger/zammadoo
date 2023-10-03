#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import atexit
import logging
from dataclasses import dataclass
from textwrap import shorten
from typing import Dict, List, Optional, Tuple, Type

import requests
from requests import HTTPError, JSONDecodeError

from .articles import Articles
from .groups import Groups
from .organizations import Organizations
from .resource import Resource
from .resources import ResourcesT
from .roles import Roles
from .tags import Tags
from .tickets import Priorities, States, Tickets
from .users import Users
from .utils import JsonType, StringKeyDict

BaseResources = ResourcesT[Resource]

LOG = logging.getLogger(__name__)


class APIException(HTTPError):
    pass


def raise_or_return_json(response: requests.Response) -> JsonType:
    try:
        response.raise_for_status()
    except HTTPError as exc:
        LOG.error("%s (%d): %s", response.reason, response.status_code, response.text)
        try:
            info = response.json()
            error = info.get("error_human") or info["error"]
            raise APIException(
                error, request=exc.request, response=exc.response
            ) from exc
        except (JSONDecodeError, KeyError):
            message = response.text
            raise HTTPError(
                message, request=exc.request, response=exc.response
            ) from exc

    try:
        return response.json()
    except JSONDecodeError:
        return response.text


class ClientMeta(type):
    def __init__(cls, name, bases, attributes):
        super().__init__(name, bases, attributes)
        mapping = getattr(cls, "resource_types")
        for base_cls in reversed(cls.mro()):
            annotations = base_cls.__dict__.get("__annotations__", {})
            mapping.update(
                (key, value)
                for key, value in annotations.items()
                if isinstance(value, type) and issubclass(value, ResourcesT)
            )


# pylint: disable=too-many-instance-attributes
class Client(metaclass=ClientMeta):
    groups: Groups
    # links: Resources
    # object_manager_attributes: Resources
    # online_notifications: Resources
    organizations: Organizations
    roles: Roles
    # ticket_article_plain: Resources
    ticket_articles: Articles
    # ticket_attachment: Resources
    ticket_priorities: Priorities
    ticket_states: States
    tickets: Tickets
    users: Users

    @dataclass
    class Pagination:
        page: int = 1
        per_page: int = 10
        expand: bool = False

    resource_types: Dict[str, Type[BaseResources]] = {}
    __resource_inst: Dict[str, BaseResources] = {}

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
        self.pagination = self.Pagination()
        self._tags = Tags(self)

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
        if self._http_token is not None:
            return
        if self._oauth2_token is not None:
            return
        if self._username is None:
            raise Client.ConfigException("Missing username in config")
        if self._password is None:
            raise Client.ConfigException("Missing password in config")

    def __getattr__(self, item) -> BaseResources:
        instance_map = self.__resource_inst
        instance = instance_map.get(item)
        if instance:
            return instance

        klass = self.resource_types.get(item)
        if not klass:
            raise AttributeError(item)
        return instance_map.setdefault(item, klass(self, item))

    @property
    def tags(self) -> Tags:
        return self._tags

    def request(
        self,
        method: str,
        *args,
        params: Optional[StringKeyDict] = None,
        json: Optional[StringKeyDict] = None,
        **kwargs,
    ):
        url = "/".join(map(str, (self.url, *args)))
        response = self.session.request(method, url, params=params, json=json, **kwargs)
        if json and LOG.level == logging.DEBUG:
            LOG.debug("[%s] %s json=%r", method, response.url, json)
        else:
            LOG.info("[%s] %s", method, response.url)
        value = raise_or_return_json(response)
        LOG.debug("[%s] returned %s", method, shorten(repr(value), width=120))
        return value

    def get(self, *args, params: Optional[StringKeyDict] = None):
        return self.request("GET", *args, params=params)

    def post(self, *args, json: Optional[StringKeyDict] = None):
        return self.request("POST", *args, json=json)

    def put(self, *args, json: Optional[StringKeyDict] = None):
        return self.request("PUT", *args, json=json)

    def delete(self, *args, json: Optional[StringKeyDict] = None):
        return self.request("DELETE", *args, json=json)
