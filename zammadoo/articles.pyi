#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from os import PathLike
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Iterator, List, Optional, Union

from . import Client
from .resource import Resource
from .resources import ResourcesT
from .tickets import Ticket
from .utils import JsonDict, JsonType

PathType = Union[str, PathLike]

class Attachment:
    id: int
    filename: str
    preferences: Dict[str, Any]
    size: int
    store_file_id: int

    def __init__(self, client: Client, content_url: str, info: JsonDict) -> None: ...
    def __getattr__(self, item): ...
    @staticmethod
    def info_from_files(*paths: PathType) -> List[Dict[str, str]]: ...
    @property
    def url(self) -> str: ...
    def view(self) -> MappingProxyType[str, JsonType]: ...
    def read_bytes(self) -> bytes: ...
    def read_text(self) -> str: ...
    def download(self, path: PathType = ...) -> Path: ...
    @property
    def encoding(self) -> Optional[str]: ...
    def iter_text(self, chunk_size: int = ...) -> Iterator[str]: ...
    def iter_bytes(self, chunk_size: int = ...) -> Iterator[bytes]: ...

class Article(Resource):
    parent: "Articles"

    attachments: List[Attachment]
    body: str
    cc: Optional[str]
    content_type: str
    created_at: datetime
    created_by: str
    from_: str
    internal: bool
    message_id: Optional[str]
    message_id_md5: Optional[str]
    subject: Optional[str]
    ticket: Ticket
    to: Optional[str]
    updated_at: datetime
    updated_by: str

class Articles(ResourcesT[Article]):
    def __init__(self, client: Client) -> None: ...
    def by_ticket(self, tid: int) -> List[Article]: ...
    def create(self, ticket_id: int, body: str, **kwargs) -> Article: ...
