#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base64 import b64encode
from datetime import datetime
from mimetypes import guess_type
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Dict, Iterable, Iterator, List, Optional

import requests
from charset_normalizer import is_binary

from .resource import Resource
from .resources import CreatableT, ResourcesT
from .utils import info_cast

if TYPE_CHECKING:
    from typing import Union

    from .client import Client
    from .tickets import Ticket
    from .users import User
    from .utils import JsonDict, PathType

    OptionalFiles = Union[None, "PathType", Iterable["PathType"]]


class Attachment:
    """Attachment(...)"""

    id: int  #:
    filename: str  #:
    preferences: Dict[str, Any]  #:
    store_file_id: int  #:

    def __init__(self, client: "Client", content_url: str, info: "JsonDict") -> None:
        self._client = client
        self._url = content_url
        self._info = info

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self._url!r}>"

    def __getattr__(self, item):
        return self._info[item]

    @property
    def size(self) -> int:
        return int(info_cast(self._info)["size"])

    @property
    def url(self) -> str:
        return self._url

    def view(self) -> "MappingProxyType[str, Any]":
        return MappingProxyType(self._info)

    @staticmethod
    def info_from_files(*paths: "PathType"):
        info_list = []
        for path in paths:
            filepath = Path(path)
            assert filepath.is_file(), f"file {filepath} does not exist"
            mime_type, encoding = guess_type(filepath, strict=True)
            raw_bytes = filepath.read_bytes()
            if mime_type is None:
                mime_type = (
                    "text/plain"
                    if encoding or not is_binary(raw_bytes)
                    else "application/octet-stream"
                )

            info_list.append(
                {
                    "filename": filepath.name,
                    "data": b64encode(raw_bytes).decode("utf-8"),
                    "mime-type": mime_type,
                }
            )
        return info_list

    def _response(self) -> requests.Response:
        response = self._client.response("GET", self._url, stream=True)
        response.raise_for_status()

        preferences = info_cast(self._info).get("preferences", {})
        response.encoding = preferences.get("Charset") or response.apparent_encoding

        return response

    def download(self, path: "PathType" = ".") -> "Path":
        filepath = Path(path)
        if filepath.is_dir():
            filepath = filepath / self.filename

        with filepath.open("wb") as fd:
            for chunk in self.iter_bytes():
                fd.write(chunk)

        return filepath

    def read_bytes(self) -> bytes:
        return self._response().content

    def read_text(self) -> str:
        return self._response().text

    def iter_text(self, chunk_size=8192):
        response = self._response()
        assert response.encoding, "content is binary only, use .iter_bytes() instead"
        return response.iter_content(chunk_size=chunk_size, decode_unicode=True)

    def iter_bytes(self, chunk_size=8192) -> Iterator[bytes]:
        return self._response().iter_content(chunk_size=chunk_size)


class Article(Resource):
    """Article(...)"""

    body: str  #:
    cc: Optional[str]  #:
    content_type: str  #:
    created_at: datetime  #:
    from_: str  #:
    internal: bool  #:
    message_id: Optional[str]  #:
    message_id_md5: Optional[str]  #:
    sender: str  #:
    subject: Optional[str]  #:
    to: Optional[str]  #:
    updated_at: datetime  #:

    @property
    def created_by(self) -> "User":
        uid = self["created_by_id"]
        return self.parent.client.users(uid)

    @property
    def origin_by(self) -> Optional["User"]:
        oid = self["origin_by_id"]
        return self.parent.client.users(oid)

    @property
    def updated_by(self) -> "User":
        uid = self["updated_by_id"]
        return self.parent.client.users(uid)

    @property
    def ticket(self) -> "Ticket":
        return self.parent.client.tickets(self["ticket_id"])

    @property
    def attachments(self) -> List[Attachment]:
        attachment_list = []
        client = self.parent.client
        for info in self["attachments"]:
            url = f"{client.url}/ticket_attachment/{self['ticket_id']}/{self._id}/{info['id']}"
            attachment = Attachment(client, url, info)
            attachment_list.append(attachment)
        return attachment_list


class Articles(CreatableT[Article], ResourcesT[Article]):
    """Articles(...)"""

    _RESOURCE_TYPE = Article

    def __init__(self, client: "Client"):
        super().__init__(client, "ticket_articles")

    def by_ticket(self, tid: int) -> List[Article]:
        items = self.client.get(self.endpoint, "by_ticket", tid)
        return [self(item["id"], info=item) for item in items]

    def create(
        self,
        ticket_id: int,
        body: str,
        files: "OptionalFiles" = None,
        **kwargs,
    ) -> Article:
        """
        Create a new ticket article.

        :param ticket_id: the ticket id where the article will be appended
        :param body: article text
        :param files: file attachments
        :param kwargs: additional article parameters
        :return: the newly created article
        """
        if files is None:
            files = ()
        elif isinstance(files, str) or not isinstance(files, Iterable):
            files = (files,)

        attachments = kwargs.pop("attachments", [])
        attachments.extend(Attachment.info_from_files(*files))
        assert all(
            attachment.keys() == {"filename", "data", "mime-type"}
            for attachment in attachments
        ), "improper attachment info"
        info = {
            "ticket_id": ticket_id,
            "body": body,
            "attachments": attachments,
            **kwargs,
        }

        return super()._create(info)
