#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os.path
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Tuple
from unittest.mock import patch

import pytest
from requests import PreparedRequest, Session

from tests.recording import ResponsePlayback, ResponseRecorder
from zammadoo import Client


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


def pytest_runtest_setup(item):
    if "no_record" in item.keywords and item.config.getoption("--record"):
        pytest.skip("disabled recording")


@pytest.fixture(scope="session")
def client_url(request):
    os.environ["CURL_CA_BUNDLE"] = "mylocalhost.crt"
    return request.config.getoption("--client-url")


@pytest.fixture(scope="session")
def api_token(request):
    http_token = request.config.getoption("--http-token")

    if os.path.exists(http_token):
        with open(http_token, encoding="utf-8") as fd:
            http_token = fd.read()

    return http_token


@pytest.fixture(scope="function")
def record_log(request) -> Tuple[Path, bool]:
    missing_only = request.config.getoption("--record-missing")
    recording = missing_only or request.config.getoption("--record")

    rpath: Path = request.path
    record_file = rpath.with_name(rpath.stem) / f"{request.function.__name__}.log"

    if (
        recording
        and missing_only
        and record_file.is_file()
        and record_file.stat().st_size
    ):
        recording = False

    return record_file, recording


@pytest.fixture(scope="function")
def recorded_session(record_log):
    session_request = Session.request
    record_file, recording = record_log

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

        def prepared_request(
            method,
            url,
            params=None,
            data=None,
            headers=None,
            cookies=None,
            files=None,
            auth=None,
            timeout=None,
            allow_redirects=True,
            proxies=None,
            hooks=None,
            stream=None,
            verify=None,
            cert=None,
            json=None,
        ) -> PreparedRequest:
            _ = (stream, verify, cert, timeout, allow_redirects, proxies)
            req = PreparedRequest()
            req.prepare(
                method=method,
                url=url,
                headers=headers,
                files=files,
                data=data,
                params=params,
                auth=auth,
                cookies=cookies,
                hooks=hooks,
                json=json,
            )
            return req

        def _request(self: Session, method, url, *args, **kwargs):
            req = prepared_request(method, url, *args, **kwargs)
            return replay.response_from_request(req)

    with patch.object(Session, "request", new=_request):
        yield

    cleanup()


@pytest.fixture(scope="function")
def zammad_api(recorded_session, client_url, api_token):
    session = Session()
    session.headers["User-Agent"] = "zammadoo pytest"
    if api_token:
        session.headers["Authorization"] = f"Token token={api_token}"

    def _request(method: str, endpoint: str, *args, **kwargs):
        response = session.request(
            method, f"{client_url}/{endpoint}#fixture", *args, **kwargs
        )
        response.raise_for_status()
        return response

    yield _request
    session.close()


@pytest.fixture(scope="function")
def temporary_resources(zammad_api):
    from zammadoo.utils import StringKeyMapping

    @contextmanager
    def _create_temporary(endpoint: str, *parameter: StringKeyMapping):
        temporary_resources = []
        for param in parameter:
            value = zammad_api("POST", f"{endpoint}", json=param).json()
            temporary_resources.append(value)

        yield temporary_resources

        for resource in temporary_resources:
            zammad_api("DELETE", f"{endpoint}/{resource['id']}")

    return _create_temporary


@pytest.fixture(scope="function")
def client(client_url, api_token) -> Client:
    return Client(client_url, http_token=api_token)


@pytest.fixture(scope="function")
def rclient(recorded_session, client) -> Generator[Client, None, None]:
    yield client
