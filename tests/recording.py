#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import re
from collections import deque
from contextlib import suppress
from mmap import ACCESS_READ, mmap
from pathlib import Path
from typing import Any, Deque, Dict, Tuple
from unittest import TestCase

from requests import PreparedRequest, Response


class ResponseRecorder:
    def __init__(self, path: Path) -> None:
        self.fd = open(path, "ab")

    def dump(self, method: str, response: Response) -> None:
        fd = self.fd
        content = response.content
        request_body: bytes = response.request.body
        extra = {}
        if request_body and request_body.startswith(b"{"):
            with suppress(json.JSONDecodeError, UnicodeDecodeError):
                extra["request_json"] = json.loads(request_body.decode("utf-8"))
        meta: Dict[str, Any] = {
            "method": method,
            "url": response.url,
            "status_code": response.status_code,
            "reason": response.reason,
            "headers": dict(
                (key, value)
                for key, value in response.headers.items()
                if re.fullmatch(r"[Cc]ontent-[A-Za-z][a-z]+", key)
            ),
            "encoding": response.encoding,
            **extra,
            "content_size": len(content),
        }

        fd.writelines((json.dumps(meta).encode("utf-8"), b"\n", content, b"\n"))

    def clear(self) -> None:
        self.fd.truncate(0)

    def close(self) -> None:
        self.fd.close()


class ResponsePlaybackError(KeyError):
    pass


class ResponsePlayback:
    MAPPING_TYPE = Dict[Tuple[str, str], Deque[Dict[str, Any]]]

    def __init__(self, path: Path) -> None:
        self.fd = fd = open(path, "rb")
        mm = mmap(fd.fileno(), 0, access=ACCESS_READ)
        self.index = self.build_index(mm)
        mm.close()

    @staticmethod
    def build_index(mm) -> MAPPING_TYPE:
        index: ResponsePlayback.MAPPING_TYPE = {}

        for line in iter(mm.readline, b""):
            if not line.strip():
                continue
            content_start = mm.tell()
            meta = json.loads(line)
            key = (meta["method"], meta["url"])
            meta["content_start"] = content_start
            index.setdefault(key, deque()).append(meta)
            mm.seek(meta["content_size"] + 1, 1)

        return index

    def response_from_request(self, request: PreparedRequest):
        assert request.method and request.url
        key = (request.method, request.url)
        try:
            meta = self.index[key].popleft()
        except KeyError as exc:
            raise ResponsePlaybackError(*exc.args) from exc

        resp = Response()
        resp.headers.update(meta.get("headers", {}))
        for item in ("url", "status_code", "encoding", "reason"):
            setattr(resp, item, meta[item])

        content_start = meta["content_start"]
        mm = mmap(
            self.fd.fileno(), content_start + meta["content_size"], access=ACCESS_READ
        )
        mm.seek(content_start)
        resp.raw = mm

        expected_json = meta.get("request_json")
        if expected_json is not None:
            request_json = json.loads(request.body.decode("utf-8"))
            TestCase().assertDictEqual(
                expected_json,
                request_json,
                "Recorded request JSON differ from current test.",
            )

        return resp

    def close(self) -> None:
        self.fd.close()
