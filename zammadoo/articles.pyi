#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from requests import Session

from .resource import ResourceListProperty as ResourceListProperty
from .resources import Resource as Resource
from .resources import ResourcesT as ResourcesT
from .tickets import Ticket
from .utils import JsonDict

class Attachment:
    id: int
    filename: str
    preferences: Dict[str, Any]
    size: int
    store_file_id: int

    def __init__(self, session: Session, content_url: str, info: JsonDict) -> None: ...
    def __getattr__(self, item): ...
    @property
    def url(self): ...
    def read_bytes(self) -> bytes: ...
    def read_text(self) -> str: ...
    def download(self, path: Union[str, Path] = ...) -> Path: ...
    @property
    def encoding(self) -> Optional[str]: ...
    def iter_text(self, chunk_size: int = ...) -> Iterator[str]: ...
    def iter_bytes(self, chunk_size: int = ...) -> Iterator[bytes]: ...

class Article(Resource):
    attachments: List[Attachment]
    body: str
    cc: str
    content_type: str
    created_at: datetime
    created_by: str
    from_: str
    internal: bool
    message_id: Optional[str]
    message_id_md5: Optional[str]
    subject: str
    ticket: Ticket
    to: str
    updated_at: datetime
    updated_by: str

class Articles(ResourcesT[Article]):
    @property
    def ticket(self): ...
    @property
    def attachments(self): ...

class ArticleListProperty(ResourceListProperty[Article]):
    def __init__(self, key: Optional[str] = ...) -> None: ...
