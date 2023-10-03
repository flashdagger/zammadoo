#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base64 import b64encode
from logging import getLogger
from mimetypes import guess_type
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import requests
from requests import Session

from .resource import Resource
from .resources import ResourcesT

if TYPE_CHECKING:
    from .utils import JsonDict


class Attachment:
    def __init__(self, session: Session, content_url: str, info: "JsonDict"):
        self._session = session
        self._content_url = content_url
        self._info = info

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self._content_url!r}>"

    def __getattr__(self, item):
        return self._info[item]

    @staticmethod
    def info_from_files(*paths):
        info_list = []
        for path in paths:
            filepath = Path(path)
            assert filepath.is_file()
            mime_type, encoding = guess_type(filepath, strict=True)
            info_list.append(
                {
                    "filename": filepath.name,
                    "data": b64encode(filepath.read_bytes()),
                    "mime-type": mime_type,
                }
            )
        return info_list

    @property
    def url(self):
        return self._content_url

    def _response(self, encoding: Optional[str] = None) -> requests.Response:
        url = self._content_url
        response = self._session.get(url, stream=True)

        # debug info
        headers = response.headers
        mapping = dict.fromkeys(("Content-Length", "Content-Type"))
        for key in mapping:
            mapping[key] = headers.get(key)
        info = ", ".join(f"{key}: {value}" for key, value in mapping.items() if value)
        getLogger("zammadoo.client").debug("[GET] %s [%s]", url, info)

        if encoding:
            response.encoding = encoding
        return response

    def download(self, path=".") -> Path:
        filepath = Path(path)
        if filepath.is_dir():
            filepath = filepath / self.filename

        with filepath.open("wb") as fd:
            for chunk in self.iter_bytes():
                fd.write(chunk)

        return filepath

    def read_bytes(self):
        return self._response().content

    def read_text(self):
        return self._response(self.encoding).text

    @property
    def encoding(self):
        preferences = self._info.get("preferences", {})
        return preferences.get("Charset")

    def iter_text(self, chunk_size=4096):
        encoding = self.encoding
        return self._response(encoding=encoding).iter_content(
            chunk_size=chunk_size, decode_unicode=bool(encoding)
        )

    def iter_bytes(self, chunk_size=4096):
        return self._response().iter_content(chunk_size=chunk_size)


class Article(Resource):
    @property
    def ticket(self):
        return self._resources.client.tickets(self["ticket_id"])

    @property
    def attachments(self):
        attachment_list = []
        client = self._resources.client
        for info in self["attachments"]:
            url = f"{client.url}/ticket_attachment/{self['ticket_id']}/{self._id}/{info['id']}"
            attachment = Attachment(client.session, url, info)
            attachment_list.append(attachment)
        return attachment_list


class Articles(ResourcesT[Article]):
    RESOURCE_TYPE = Article

    def by_ticket(self, tid: int):
        items = self.client.get(self.endpoint, "by_ticket", tid)
        return [self(item["id"], info=item) for item in items]
