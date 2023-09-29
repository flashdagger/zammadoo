#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from typing import TYPE_CHECKING, Dict, List, Optional

from .resource import ResourceListProperty
from .resources import Resource, ResourcesT
from .utils import StringKeyDict

if TYPE_CHECKING:
    pass


ItemDict = Dict[str, List[str]]
ItemList = List[StringKeyDict]


class Article(Resource):
    @property
    def ticket(self):
        return self._resources.client.tickets(self["ticket_id"])


class Articles(ResourcesT[Article]):
    RESOURCE_TYPE = Article


class ArticleListProperty(ResourceListProperty[Article]):
    def __init__(self, key: Optional[str] = None):
        super().__init__(endpoint="ticket_articles", key=key or "")
