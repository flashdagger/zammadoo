#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os.path
from http.client import responses
from mmap import mmap, ACCESS_READ
from pathlib import Path
from typing import Any, Dict, Generator, Tuple
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
        with open(http_token, "utf-8") as fd:
            http_token = fd.read()

    client = Client(client_url, http_token=http_token)
    client.session.verify = "mylocalhost.crt"
    return client


class FileWriter:
    def __init__(self, path: Path) -> None:
        self.fd = open(path, "ab")

    def append(self, key: str, data: bytes) -> None:
        assert "\0" not in key
        fd = self.fd
        fd.writelines((f"{key}\0{len(data)}\n".encode("utf-8"), data, b"\n"))

    def clear(self) -> None:
        self.fd.truncate(0)

    def close(self) -> None:
        self.fd.close()


class FileReader:
    def __init__(self, path: Path) -> None:
        self.fd = fd = open(path, "rb")
        mm = mmap(fd.fileno(), 0, access=ACCESS_READ)
        self.index = self.build_index(mm)
        mm.close()

    @staticmethod
    def build_index(mm) -> Dict[str, Tuple[int, int]]:
        index: Dict[str, Tuple[int, int]] = {}

        for line in iter(mm.readline, b""):
            key, bdata_len = line.decode("utf-8").rsplit("\0", maxsplit=1)
            data_len = int(bdata_len)
            index[key] = (mm.tell(), data_len)
            mm.seek(int(bdata_len) + 1, 1)

        return index

    def __getitem__(self, item: str) -> bytes:
        offset, length = self.index[item]
        fd = self.fd
        fd.seek(offset)
        return fd.read(length)

    def close(self) -> None:
        self.fd.close()


@pytest.fixture(scope="function")
def rclient(request: pytest.FixtureRequest, client) -> Generator[Client, None, None]:
    session_request = Session.request
    recording = request.config.getoption("--record")

    rpath = request.path
    record_file = rpath.with_name(rpath.stem) / f"{request.function.__name__}.log"

    def serialize(method: str, url: str, params: Dict[str, Any]) -> str:
        param_items = params.items() if isinstance(params, dict) else params or ()
        query = urlencode(sorted(param_items))
        join = "?" if query else ""
        return f"{method} {url}{join}{query}"

    if recording:
        record_file.parent.mkdir(exist_ok=True)
        recorder = FileWriter(record_file)
        recorder.clear()

        def cleanup() -> None:
            recorder.close()

        def _request(self: Session, method, url, *args, **kwargs):
            params = kwargs.get("params", None)
            response = session_request(self, method, url, *args, **kwargs)
            key = serialize(method, url, params)
            data = b"\0".join(
                (bytes(str(response.status_code), "ascii"), response.content)
            )
            recorder.append(key, data)
            return response

    else:
        replay = FileReader(record_file)

        def cleanup() -> None:
            replay.close()

        def _request(self: Session, method, url, *args, **kwargs):
            params = kwargs.pop("params", None)

            response = Response()
            key = serialize(method, url, params)
            status, response._content = replay[key].split(b"\0", maxsplit=1)
            status_code = int(status)
            response.status_code = status_code
            response.reason = responses[status_code]

            return response

    with patch.object(Session, "request", new=_request):
        yield client

    cleanup()
