#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import os.path
from collections import deque
from mmap import ACCESS_READ, mmap
from pathlib import Path
from typing import Any, Deque, Dict, Generator, Tuple
from unittest.mock import patch

import pytest
from requests import PreparedRequest, Response, Session

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
        "--record-missing",
        action="store_true",
        default=False,
        help="run tests without logfile against a zammad server instance and record the responses",
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


class FileWriter:
    def __init__(self, path: Path) -> None:
        self.fd = open(path, "ab")

    def append(self, method: str, response: Response) -> None:
        fd = self.fd
        content = response.content
        meta = {"method": method}
        for item in ("url", "status_code", "encoding", "reason"):
            meta[item] = getattr(response, item)
        meta["content_size"] = len(content)
        fd.writelines((json.dumps(meta).encode("utf-8"), b"\n", content, b"\n"))

    def clear(self) -> None:
        self.fd.truncate(0)

    def close(self) -> None:
        self.fd.close()


class FileReader:
    MAPPING_TYPE = Dict[Tuple[str, str], Deque[Dict[str, Any]]]

    def __init__(self, path: Path) -> None:
        self.fd = fd = open(path, "rb")
        mm = mmap(fd.fileno(), 0, access=ACCESS_READ)
        self.index = self.build_index(mm)
        mm.close()

    @staticmethod
    def build_index(mm) -> MAPPING_TYPE:
        index: FileReader.MAPPING_TYPE = {}

        for line in iter(mm.readline, b""):
            content_start = mm.tell()
            meta = json.loads(line)
            key = (meta["method"], meta["url"])
            meta["content_start"] = content_start
            index.setdefault(key, deque()).append(meta)
            mm.seek(meta["content_size"] + 1, 1)

        return index

    def response(self, request):
        key = (request.method, request.url)
        meta = self.index[key].popleft()

        resp = Response()
        for item in ("url", "status_code", "encoding", "reason"):
            setattr(resp, item, meta[item])

        content_start = meta["content_start"]
        mm = mmap(
            self.fd.fileno(), content_start + meta["content_size"], access=ACCESS_READ
        )
        mm.seek(content_start)
        resp.raw = mm

        return resp

    def close(self) -> None:
        self.fd.close()


@pytest.fixture(scope="function")
def client(request) -> Client:
    client_url = request.config.getoption("--client-url")
    http_token = request.config.getoption("--http-token")

    if os.path.exists(http_token):
        with open(http_token, encoding="utf-8") as fd:
            http_token = fd.read()

    client = Client(client_url, http_token=http_token)
    client.session.verify = "mylocalhost.crt"
    return client


@pytest.fixture(scope="function")
def rclient(request: pytest.FixtureRequest, client) -> Generator[Client, None, None]:
    session_request = Session.request
    missing_only = request.config.getoption("--record-missing")
    recording = missing_only or request.config.getoption("--record")

    rpath = request.path
    record_file = rpath.with_name(rpath.stem) / f"{request.function.__name__}.log"
    if recording and missing_only and record_file.is_file():
        recording = False

    if recording:
        record_file.parent.mkdir(exist_ok=True)
        recorder = FileWriter(record_file)
        recorder.clear()

        def cleanup() -> None:
            recorder.close()

        def _request(self: Session, method, url, *args, **kwargs):
            response = session_request(self, method, url, *args, **kwargs)
            recorder.append(method, response)
            return response

    else:
        replay = FileReader(record_file)

        def cleanup() -> None:
            replay.close()

        def _request(self: Session, method, url, *args, **kwargs):
            req = PreparedRequest()
            req.prepare(method=method, url=url, *args, **kwargs)
            return replay.response(req)

    with patch.object(Session, "request", new=_request):
        yield client

    cleanup()
