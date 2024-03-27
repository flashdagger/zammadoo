#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from base64 import b64encode
from mimetypes import guess_type
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, Iterator, List, Optional, Union

import requests
from charset_normalizer import is_binary

from .resource import OptionalUserProperty, Resource, UserProperty
from .resources import CreatableT, ResourcesT
from .time_accountings import TimeAccounting
from .utils import AttributeT, DateTime, FrozenInfo

if TYPE_CHECKING:
    from os import PathLike

    from .client import Client
    from .tickets import Ticket
    from .utils import JsonDict

    PathType = Union[str, PathLike[Any]]
    OptionalFiles = Union[None, "PathType", Iterable["PathType"]]


class Attachment(FrozenInfo):
    """Attachment(...)"""

    id: int  #:
    filename: str  #:
    preferences: Dict[str, Any]  #:
    store_file_id: int  #:
    url: str  #: attachment content url

    def __init__(self, client: "Client", content_url: str, info: "JsonDict") -> None:
        self._client = client
        self.url = content_url
        super().__init__(info)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.url!r}>"

    @property
    def size(self) -> int:
        """attachment size in bytes"""
        return int(self._info["size"])

    @staticmethod
    def info_from_files(*paths: "PathType"):
        """
        returns a list of dicts that can be used for the ``attachments`` property when
        `creating articles <https://docs.zammad.org/en/latest/api/ticket/articles.html#create>`_

        :param paths: one or multiple paths of the attachment files
        """
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
        response = self._client.response("GET", self.url, stream=True)
        response.raise_for_status()

        preferences = self._info.get("preferences", {})
        response.encoding = preferences.get("Charset") or response.apparent_encoding

        return response

    def download(self, path: "PathType" = ".", raise_if_exists=False) -> "Path":
        """
        Downloads the attachment file to the filesystem.

        :raises: :exc:`FileExistsError`

        :param path: optional download location (directory or full file path)
        :param raise_if_exists: raises :exc:`FileExistsError` if destination file exists
        :return: the path of the downloaded attachment file
        """
        filepath = Path(path)
        if filepath.is_dir():
            filepath = filepath / self.filename

        if raise_if_exists and filepath.exists():
            raise FileExistsError(f"File already exists: {str(filepath)!r}")

        with filepath.open("wb") as fd:
            for chunk in self.iter_bytes():
                fd.write(chunk)

        return filepath

    def read_bytes(self) -> bytes:
        """Return the attachment content as bytes."""
        return self._response().content

    def read_text(self) -> str:
        """Return the attachment content as string."""
        return self._response().text

    def iter_text(self, chunk_size=8192) -> Iterator[str]:
        """
        Iterates over the decoded attachment text content.

        :param chunk_size: maximum chunk size in bytes
        """
        response = self._response()
        assert response.encoding, "content is binary only, use .iter_bytes() instead"
        return response.iter_content(chunk_size=chunk_size, decode_unicode=True)

    def iter_bytes(self, chunk_size=8192) -> Iterator[bytes]:
        """
        Iterates over the attachment binary content.

        :param chunk_size: maximum chunk size in bytes
        """
        return self._response().iter_content(chunk_size=chunk_size)


class Article(Resource):
    """Article(...)"""

    body: str  #:
    cc: Optional[str]  #:
    content_type: str  #:
    internal: bool  #:
    message_id: Optional[str]  #:
    message_id_md5: Optional[str]  #:
    parent: "Articles"
    sender: str  #:
    subject: Optional[str]  #:
    time_unit: Optional[str]  #:
    to: Optional[str]  #:

    created_at = DateTime()
    created_by = UserProperty()
    from_ = AttributeT[str]("from")
    origin_by = OptionalUserProperty()
    updated_at = DateTime()
    updated_by = UserProperty()

    @property
    def ticket(self) -> "Ticket":
        tid: int = self["ticket_id"]
        return self.parent.client.tickets(tid)

    @property
    def attachments(self) -> List[Attachment]:
        """A list of the articles attachments."""
        client = self.parent.client
        attachment_url = f"{client.url}/ticket_attachment/{self['ticket_id']}/{self.id}"
        return [
            Attachment(client, f"{attachment_url}/{info['id']}", info)
            for info in self["attachments"]
        ]

    def create_or_update_time_accounting(
        self, time_unit: Union[str, float], **kwargs
    ) -> "TimeAccounting":
        """
        Create accounted time for ticket article.
        If time accounting already exists, it will be updated.

        :param time_unit: accounted time units
        :param kwargs: type(`str`) or type_id(`int`)
        :rtype: :class:`TimeAccounting`
        """
        aid = self.id
        kwargs["ticket_article_id"] = aid

        ticket = self.ticket
        for accounting in ticket.time_accountings():
            if accounting["ticket_article_id"] == aid:
                return accounting.update(time_unit=str(time_unit), **kwargs)

        return self.ticket.create_time_accounting(time_unit, **kwargs)


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
