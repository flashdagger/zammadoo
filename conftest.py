#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os.path
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from requests import Response, Session

from zammadoo import Client
from zammadoo.resource import Resource


def pytest_addoption(parser):
    parser.addoption(
        "--record",
        action="store_true",
        default=False,
        help="run the tests against a zammad server instance and record the responses",
    )
    parser.addoption(
        "--client-url", default="https://localhost/api/v1", help="the zammad server url"
    )
    parser.addoption(
        "--http-token",
        default="<token>",
        help="zammad server HTTP Authentication token",
    )


def resource(items=()):
    def initialize(self):
        self._info["id"] = self._id
        self._info.update(items)

    return patch.object(Resource, "_initialize", new=initialize)


@pytest.fixture(scope="session")
def client(request) -> Client:
    client_url = request.config.getoption("--client-url")
    http_token = request.config.getoption("--http-token")

    if os.path.exists(http_token):
        with open(http_token) as fd:
            http_token = fd.read()

    client = Client(client_url, http_token=http_token)
    client.session.verify = "mylocalhost.crt"
    return client


class FileDict:
    def __init__(self, path: Path) -> None:
        self.fd = open(path, "a+")
        self.fd.seek(0)  # jump to beginning of file
        self.line = 0

    def __setitem__(self, key: str, value: str) -> None:
        fd = self.fd
        fd.seek(0, 2)  # jump to end of file
        print(key, value, file=fd)
        self.line = 0

    def __getitem__(self, key: str) -> str:
        fd = self.fd
        wrapped = False
        last_line = self.line

        while True:
            for line in fd:
                if wrapped and self.line == last_line:
                    break

                self.line += 1
                if line.startswith(key):
                    return line[len(key) + 1 : -1]

            if wrapped:
                break

            fd.seek(0)
            self.line = 0
            wrapped = True

        raise KeyError(key)

    def clear(self) -> None:
        self.fd.truncate(0)

    def close(self) -> None:
        self.fd.close()


@pytest.fixture(scope="function")
def rclient(request: pytest.FixtureRequest, client) -> Generator[Client, None, None]:
    session_request = Session.request
    recording = request.config.getoption("--record")

    rpath = request.path
    record_file = rpath.with_name(rpath.stem) / f"{request.function.__name__}.log"

    if recording:
        record_file.parent.mkdir(exist_ok=True)

    recorder = FileDict(record_file)

    if recording:
        recorder.clear()

    def serialize(method: str, url: str, params: Dict[str, Any]) -> str:
        param_items = params.items() if isinstance(params, dict) else params or ()
        query = urlencode(sorted(param_items))
        join = "?" if query else ""
        return f"{method} {url}{join}{query}"

    def replay_request(_self, method, url, *_args, **kwargs):
        params = kwargs.pop("params", None)
        key = serialize(method, url, params)
        status, content = recorder[key].split(maxsplit=1)
        response = Response()
        response.status_code = int(status)
        response._content = content.encode()

        return response

    def record_request(self: Session, method, url, *args, **kwargs):
        params = kwargs.get("params", None)
        response = session_request(self, method, url, *args, **kwargs)
        key = serialize(method, url, params)
        recorder[key] = f"{response.status_code} {response.text}"
        return response

    with patch.object(
        Session, "request", new=record_request if recording else replay_request
    ):
        yield client

    recorder.close()
