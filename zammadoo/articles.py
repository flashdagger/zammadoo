#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from requests import Session

from .resource import ResourceListProperty
from .resources import Resource, ResourcesT

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

    @property
    def url(self):
        return self._content_url

    def _response(self, encoding: Optional[str] = None):
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

    def download(self, path: Union[str, Path] = ".") -> Path:
        filepath: Path = Path(path)
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

    def iter_bytes(self, chunk_size=1024):
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


class ArticleListProperty(ResourceListProperty[Article]):
    def __init__(self, key: Optional[str] = None):
        super().__init__(endpoint="ticket_articles", key=key or "")
