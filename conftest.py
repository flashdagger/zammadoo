#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os.path
from typing import Generator
from unittest.mock import patch

import pytest
from requests import PreparedRequest, Session

from tests.recording import ResponseRecorder, ResponsePlayback
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


@pytest.fixture(scope="function")
def client(request) -> Client:
    client_url = request.config.getoption("--client-url")
    http_token = request.config.getoption("--http-token")

    if os.path.exists(http_token):
        with open(http_token, encoding="utf-8") as fd:
            http_token = fd.read()

    _client = Client(client_url, http_token=http_token)
    _client.session.verify = "mylocalhost.crt"
    return _client


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
        recorder = ResponseRecorder(record_file)
        recorder.clear()

        def cleanup() -> None:
            recorder.close()

        def _request(self: Session, method, url, *args, **kwargs):
            response = session_request(self, method, url, *args, **kwargs)
            recorder.dump(method, response)
            return response

    else:
        replay = ResponsePlayback(record_file)

        def cleanup() -> None:
            replay.close()

        def _request(self: Session, method, url, *args, **kwargs):
            req = PreparedRequest()
            req.prepare(method, url, *args, **kwargs)
            return replay.response_from_request(req)

    with patch.object(Session, "request", new=_request):
        yield client

    cleanup()
