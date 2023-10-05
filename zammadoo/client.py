#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import atexit
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from textwrap import shorten
from typing import Optional, Sequence, Tuple, Union, cast

import requests
from requests import HTTPError, JSONDecodeError, Response

from .articles import Articles
from .groups import Groups
from .organizations import Organizations
from .roles import Roles
from .tags import Tags
from .tickets import Priorities, States, Tickets
from .users import Users
from .utils import JsonType, StringKeyDict

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
        return cast(JsonType, response.json())
    except JSONDecodeError:
        return response.text


class Client:
    """
    The root class that interacts with the REST API.

    Almost every object keeps the initialized instance of Client as reference.

    Example::

        from zammadoo import Client

        client = Client("https://myhost.com/api/v1/", username="<username>", password="<mysecret>")

    """

    # links: Resources
    # object_manager_attributes: Resources
    # online_notifications: Resources
    # ticket_article_plain: Resources
    # attachment: Resources

    @cached_property
    def groups(self) -> Groups:
        """managing the /groups endpoint"""
        return Groups(self)

    @cached_property
    def organizations(self) -> Organizations:
        """managing the /organizations endpoint"""
        return Organizations(self)

    @cached_property
    def roles(self) -> Roles:
        """managing the /roles endpoint"""
        return Roles(self)

    @cached_property
    def tags(self) -> Tags:
        """managing the /tags /tag_list and /tag_search endpoint"""
        return Tags(self)

    @cached_property
    def ticket_articles(self) -> Articles:
        """managing the /ticket_articles endpoint"""
        return Articles(self)

    @cached_property
    def ticket_priorities(self) -> Priorities:
        """managing the /ticket_priorities endpoint"""
        return Priorities(self)

    @cached_property
    def ticket_states(self) -> States:
        """managing the /ticket_states endpoint"""
        return States(self)

    @cached_property
    def tickets(self) -> Tickets:
        """managing the /tickets endpoint"""
        return Tickets(self)

    @cached_property
    def users(self) -> Users:
        """managing the ``/users`` endpoint"""
        return Users(self)

    @dataclass
    class Pagination:
        page: int = 1
        per_page: int = 10
        expand: bool = False

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        url: str,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        http_token: Optional[str] = None,
        oauth2_token: Optional[str] = None,
        additional_headers: Sequence[Tuple[str, str]] = (),
    ) -> None:
        """
        For authentication use either username and password or http_token or oauth2_token

        :param url: the zammad API url like ``https://myhost.com/api/v1``
        :type url: string
        :param username: the username for HTTP Basic Authentication
        :type username: string
        :param password: the password for HTTP Basic Authentication
        :type password: string
        :param http_token: access token when using HTTP Token Authentication
        :type http_token: string
        :param oauth2_token: access token when using OAuth 2 Authentication
        :type oauth2_token: string
        :param additional_headers: additional name, value pairs that will be
                appended to the requests header ``[(name, value), ...]``
        :type additional_headers:

        :raises ValueError: When authentication settings are not correct.


        """
        self.url = url.rstrip("/")
        self.pagination = self.Pagination()

        def check_config() -> None:
            if http_token is not None:
                return
            if oauth2_token is not None:
                return
            if username is None:
                raise TypeError("Missing username in config")
            if password is None:
                raise TypeError("Missing password in config")

        check_config()
        self.session = requests.Session()
        atexit.register(self.session.close)
        self.session.headers["User-Agent"] = "Zammad API Python"
        if http_token:
            self.session.headers["Authorization"] = f"Token token={http_token}"
        elif oauth2_token:
            self.session.headers["Authorization"] = f"Bearer {oauth2_token}"
        elif username and password:
            self.session.auth = (username, password)
        else:
            raise ValueError("Invalid Authentication information in config")

        self.session.headers.update(additional_headers)

    @contextmanager
    def impersonation_of(self, user: Union[str, int]):
        try:
            self.session.headers["X-On-Behalf-Of"] = str(user)
            yield
        finally:
            self.session.headers.pop("X-On-Behalf-Of", None)

    def request(
        self,
        method: str,
        *args,
        params: Optional[StringKeyDict] = None,
        json: Optional[StringKeyDict] = None,
        **kwargs,
    ):
        url = "/".join(map(str, (self.url, *args)))
        response = self.response(method, url, json=json, params=params, **kwargs)
        value = raise_or_return_json(response)
        LOG.debug("[%s] returned %s", method, shorten(repr(value), width=120))
        return value

    def response(
        self,
        method: str,
        url: str,
        params: Optional[StringKeyDict] = None,
        json: Optional[StringKeyDict] = None,
        **kwargs,
    ) -> Response:
        response = self.session.request(method, url, params=params, json=json, **kwargs)
        if kwargs.get("stream") and LOG.level == logging.DEBUG:
            headers = response.headers
            mapping = dict.fromkeys(("Content-Length", "Content-Type"))
            for key in mapping:
                mapping[key] = headers.get(key)
            info = ", ".join(
                f"{key}: {value}" for key, value in mapping.items() if value
            )
            LOG.debug("[%s] %s [%s]", method, response.url, info)
        elif json and LOG.level == logging.DEBUG:
            LOG.debug("[%s] %s json=%r", method, response.url, json)
        else:
            LOG.info("[%s] %s", method, response.url)
        return response

    def get(self, *args, params: Optional[StringKeyDict] = None):
        return self.request("GET", *args, params=params)

    def post(self, *args, json: Optional[StringKeyDict] = None):
        return self.request("POST", *args, json=json)

    def put(self, *args, json: Optional[StringKeyDict] = None):
        return self.request("PUT", *args, json=json)

    def delete(self, *args, json: Optional[StringKeyDict] = None):
        return self.request("DELETE", *args, json=json)
