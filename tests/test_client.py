#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re

import pytest

from zammadoo import APIException


def test_server_version(rclient):
    assert re.match(r"[5-7]\.\d+(?:\.[\w-]+)+", rclient.server_version)


def test_raise_api_exception(rclient):
    with pytest.raises(APIException, match="No route matches") as exc:
        rclient.get()

    assert exc.value.response.status_code == 404


def test_params_bool_is_lowercase(rclient):
    from urllib.parse import parse_qs, urlsplit

    response = rclient.response(
        "GET", rclient.url, params={"is_true": True, "is_false": False}
    )
    mapping = parse_qs(urlsplit(response.url).query)
    assert mapping["is_true"] == ["true"]
    assert mapping["is_false"] == ["false"]


def test_logging(caplog, rclient):
    import logging

    api_url = rclient.url

    with caplog.at_level(logging.DEBUG, logger="zammadoo"):
        rclient.response("GET", rclient.url, params={"foo": "bar"})
        rclient.response("GET", rclient.url, json={"foo": "bar"})
        rclient.response("GET", rclient.url, stream=True)

    assert caplog.record_tuples == [
        ("zammadoo", logging.INFO, f"HTTP:GET {api_url}?foo=bar"),
        (
            "zammadoo",
            logging.DEBUG,
            f"HTTP:GET {api_url} json={{'foo': 'bar'}}",
        ),
        (
            "zammadoo",
            logging.DEBUG,
            f"HTTP:GET {api_url} [Content-Type: application/json; charset=utf-8]",
        ),
    ]


def test_raises_http_exception(rclient):
    from requests import HTTPError

    from zammadoo.client import raise_or_return_json

    response = rclient.response("GET", "https://httpbin.org/status/404", verify=False)
    with pytest.raises(HTTPError):
        raise_or_return_json(response)


def test_return_text_if_not_json(rclient):
    from zammadoo.client import raise_or_return_json

    response = rclient.response("GET", "https://httpbin.org/status/200", verify=False)
    assert raise_or_return_json(response) == ""


def test_http_auth(recorded_session):
    from zammadoo import Client

    client = Client("https://httpbin.org", http_auth=("myuser", "mysecret"))
    answer = client.request("GET", "basic-auth", "myuser", "mysecret", verify=False)
    assert answer == {"authenticated": True, "user": "myuser"}

    answer = client.request(
        "GET", "hidden-basic-auth", "myuser", "mysecret", verify=False
    )
    assert answer == {"authenticated": True, "user": "myuser"}


def test_oauth2_token(recorded_session):
    from zammadoo import Client

    client = Client("https://httpbin.org", oauth2_token="AbCdEf123456")
    answer = client.request("GET", "bearer", verify=False)
    assert answer == {"authenticated": True, "token": "AbCdEf123456"}


def test_raise_if_not_authentication_provided():
    from zammadoo import Client

    with pytest.raises(TypeError, match="needs an authentication parameter"):
        Client("https://localhost")


def test_impersonation_of(rclient):
    users = rclient.users

    with rclient.impersonation_of(1):
        assert users.me().id == 1

        with rclient.impersonation_of(2):
            assert users.me().id == 2

        assert users.me().id == 1
