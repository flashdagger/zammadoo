#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base64 import b64encode
from mimetypes import guess_type
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Optional

import requests

from .resource import Resource
from .resources import Creatable, ResourcesT

if TYPE_CHECKING:
    pass


class Attachment:
    def __init__(self, client, content_url, info):
        self._client = client
        self._url = content_url
        self._info = info

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self._url!r}>"

    def __getattr__(self, item):
        return self._info[item]

    @staticmethod
    def info_from_files(*paths):
        info_list = []
        for path in paths:
            filepath = Path(path)
            assert filepath.is_file()
            mime_type, _encoding = guess_type(filepath, strict=True)
            info_list.append(
                {
                    "filename": filepath.name,
                    "data": b64encode(filepath.read_bytes()),
                    "mime-type": mime_type,
                }
            )
        return info_list

    def view(self):
        return MappingProxyType(self._info)

    @property
    def url(self):
        return self._url

    def _response(self, encoding: Optional[str] = None) -> requests.Response:
        response = self._client.response("GET", self._url, stream=True)
        response.raise_for_status()
        if encoding:
            response.encoding = encoding

        return response

    def download(self, path="."):
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

    def iter_text(self, chunk_size=8192):
        response = self._response(encoding=self.encoding)
        assert response.encoding, "content is binary only, use .iter_bytes() instead"
        return response.iter_content(chunk_size=chunk_size, decode_unicode=True)

    def iter_bytes(self, chunk_size=8192):
        return self._response().iter_content(chunk_size=chunk_size)


class Article(Resource):
    @property
    def ticket(self):
        return self.parent.client.tickets(self["ticket_id"])

    @property
    def attachments(self):
        attachment_list = []
        client = self.parent.client
        for info in self["attachments"]:
            url = f"{client.url}/ticket_attachment/{self['ticket_id']}/{self._id}/{info['id']}"
            attachment = Attachment(client, url, info)
            attachment_list.append(attachment)
        return attachment_list


class Articles(Creatable, ResourcesT[Article]):
    RESOURCE_TYPE = Article

    def __init__(self, client):
        super().__init__(client, "ticket_articles")

    def by_ticket(self, tid: int):
        items = self.client.get(self.endpoint, "by_ticket", tid)
        return [self(item["id"], info=item) for item in items]

    def create(self, ticket_id, body, **kwargs):
        info = {
            "ticket_id": ticket_id,
            "body": body,
            **kwargs,
        }
        return super()._create(info)
