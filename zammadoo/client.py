#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import atexit
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from textwrap import shorten
from typing import TYPE_CHECKING, Optional, Sequence, Tuple, Union, cast

import requests
from requests import HTTPError, JSONDecodeError, Response

from .articles import Articles
from .groups import Groups
from .organizations import Organizations
from .roles import Roles
from .tags import Tags
from .tickets import Priorities, States, Tickets
from .users import Users
from .utils import info_cast

if TYPE_CHECKING:
    from .utils import JsonType, StringKeyDict


LOG = logging.getLogger(__name__)


class APIException(HTTPError):
    """APIException(...)

    Raised when the API server indicates an error.
    """

    def __init__(self, error: str, *args, response: Response, **kwargs):
        LOG.error("%s: %s", self.__class__.__name__, error)
        super().__init__(error, *args, response=response, **kwargs)


@dataclass
class Pagination:
    page: int = 1
    per_page: int = 10
    expand: bool = False


def raise_or_return_json(response: requests.Response) -> "JsonType":
    try:
        response.raise_for_status()
    except HTTPError as exc:
        try:
            info = response.json()
            exception: HTTPError = APIException(
                info.get("error_human") or info["error"],
                request=exc.request,
                response=exc.response,
            )
        except (JSONDecodeError, KeyError):
            message = response.text
            LOG.error(
                "HTTP:%d (%s): %s", response.status_code, response.reason, message
            )
            exception = HTTPError(message, request=exc.request, response=exc.response)
        raise exception from exc

    try:
        return cast("JsonType", response.json())
    except JSONDecodeError:
        return response.text


class Client:
    """
    The root class to interact with the *REST API*.

    Almost every object keeps the initialized instance of :class:`Client` as reference.

    *Example*::

        from zammadoo import Client

        client = Client("https://myhost.com/api/v1/", username="<username>", password="<mysecret>")

    """

    @cached_property
    def groups(self) -> Groups:
        """Manages the ``/groups`` endpoint."""
        return Groups(self)

    @cached_property
    def organizations(self) -> Organizations:
        """Manages the ``/organizations`` endpoint."""
        return Organizations(self)

    @cached_property
    def roles(self) -> Roles:
        """Manages the ``/roles`` endpoint."""
        return Roles(self)

    @cached_property
    def tags(self) -> Tags:
        """Manages the ``/tags``, ``/tag_list``, ``/tag_search`` endpoint."""
        return Tags(self)

    @cached_property
    def ticket_articles(self) -> Articles:
        """Manages the ``/ticket_articles`` endpoint."""
        return Articles(self)

    @cached_property
    def ticket_priorities(self) -> Priorities:
        """Manages the ``/ticket_priorities`` endpoint."""
        return Priorities(self)

    @cached_property
    def ticket_states(self) -> States:
        """Manages the ``/ticket_states`` endpoint."""
        return States(self)

    @cached_property
    def tickets(self) -> Tickets:
        """Manages the ``/tickets`` endpoint."""
        return Tickets(self)

    @cached_property
    def users(self) -> Users:
        """Manages the ``/users`` endpoint."""
        return Users(self)

    def __init__(
        self,
        url: str,
        *,
        http_auth: Optional[Tuple[str, str]] = None,
        http_token: Optional[str] = None,
        oauth2_token: Optional[str] = None,
        additional_headers: Sequence[Tuple[str, str]] = (),
    ) -> None:
        """
        For authentication use either ``http_auth`` or ``http_token`` or ``oauth2_token``.

        :param url: the zammad API url (e.g. ``https://myhost.com/api/v1``)
        :param http_auth: username and password for HTTP Basic Authentication
        :param http_token: access token when using HTTP Token Authentication
        :param oauth2_token: access token when using OAuth 2 Authentication
        :param additional_headers: additional name, value pairs that will be
                appended to the requests header ``[(name, value), ...]``
        :raises: :exc:`ValueError` if authentication settings are missing.


        """
        self.url = url.rstrip("/")
        self.pagination = Pagination()
        self.session = requests.Session()
        atexit.register(self.session.close)
        self.session.headers["User-Agent"] = "zammadoo Python client"
        if http_token:
            self.session.headers["Authorization"] = f"Token token={http_token}"
        elif oauth2_token:
            self.session.headers["Authorization"] = f"Bearer {oauth2_token}"
        elif http_auth:
            self.session.auth = http_auth
        else:
            raise TypeError(f"{self.__class__} needs an authentication parameter.")

        self.session.headers.update(additional_headers)

    @contextmanager
    def impersonation_of(self, user: Union[str, int]):
        """
        Temporarily perform requests on behalf of another user.

        To be used as context manager::

            with client.impersonation_of(1):
                print(client.users.me().id)  # output: 1


        :param user: user id or login_name
        """
        headers = self.session.headers
        restore_value = headers.pop("X-On-Behalf-Of", None)
        try:
            headers["X-On-Behalf-Of"] = str(user)
            yield
        finally:
            if restore_value is None:
                self.session.headers.pop("X-On-Behalf-Of", None)
            else:
                headers["X-On-Behalf-Of"] = restore_value

    def request(
        self,
        method: str,
        *args,
        params: Optional["StringKeyDict"] = None,
        json: Optional["StringKeyDict"] = None,
        **kwargs,
    ):
        """
        Perform a request on the API URL.

        :param method: HTTP method: e.g. ``GET``, ``POST``, ``PUT``, ``DELETE``
        :param args: endpoint specifiers
        :param params: URL parameter (usually for ``GET``)
        :param json: data as dictionary (usually for ``POST`` or ``PUT``)
        :param kwargs: additional parameters passed to ``request()``
        :returns: the server JSON response
        :rtype: StringKeyDict

        :raises: :exc:`APIException`, :class:`requests.HTTPError`
        """
        url = "/".join(map(str, (self.url, *args)))
        response = self.response(method, url, json=json, params=params, **kwargs)
        value = raise_or_return_json(response)
        LOG.debug("HTTP:%s returned %s", method, shorten(repr(value), width=120))
        return value

    def response(
        self,
        method: str,
        url: str,
        params: Optional["StringKeyDict"] = None,
        json: Optional["StringKeyDict"] = None,
        **kwargs,
    ) -> Response:
        """
        Perform a request on the API URL.

        :param method: the HTTP method (e.g. ``GET``, ``POST``, ``PUT``, ``DELETE``)
        :param url: full resource URL
        :param params: parameter that get urlencoded (usually for ``GET``)
        :param json: data as dictionary (usually for ``POST`` or ``PUT``)
        :param kwargs: additional parameters passed to ``request()``
        :rtype: :class:`requests.Response`
        """
        response = self.session.request(method, url, params=params, json=json, **kwargs)
        if kwargs.get("stream") and LOG.level == logging.DEBUG:
            headers = response.headers
            mapping = dict.fromkeys(("Content-Length", "Content-Type"))
            for key in mapping:
                mapping[key] = headers.get(key)
            info = ", ".join(
                f"{key}: {value}" for key, value in mapping.items() if value
            )
            LOG.debug("HTTP:%s %s [%s]", method, response.url, info)
        elif json and LOG.level == logging.DEBUG:
            LOG.debug("HTTP:%s %s json=%r", method, response.url, json)
        else:
            LOG.info("HTTP:%s %s", method, response.url)
        return response

    def get(self, *args, params: Optional["StringKeyDict"] = None):
        """shortcut for :meth:`request` with parameter ``("GET", *args, params)``"""
        return self.request("GET", *args, params=params)

    def post(self, *args, json: Optional["StringKeyDict"] = None):
        """shortcut for :meth:`request` with parameter ``("POST", *args, json)``"""
        return self.request("POST", *args, json=json)

    def put(self, *args, json: Optional["StringKeyDict"] = None):
        """shortcut for :meth:`request` with parameter ``("PUT", *args, json)``"""
        return self.request("PUT", *args, json=json)

    def delete(self, *args, json: Optional["StringKeyDict"] = None):
        """shortcut for :meth:`request` with parameter ``("DELETE", *args, json)``"""
        return self.request("DELETE", *args, json=json)

    @cached_property
    def server_version(self) -> str:
        """the Zammad server version"""
        return info_cast(self.get("version"))["version"]
