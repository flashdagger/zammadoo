#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from datetime import datetime
from typing import Optional

from .resource import ResourceListProperty as ResourceListProperty
from .resources import Resource as Resource
from .resources import ResourcesT as ResourcesT
from .tickets import Ticket


class Article(Resource):
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
    RESOURCE_TYPE = Article

class ArticleListProperty(ResourceListProperty[Article]):
    def __init__(self, key: Optional[str] = ...) -> None: ...
