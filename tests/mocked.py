#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from unittest.mock import patch

import pytest

from zammadoo import Client
from zammadoo.resource import Resource

CLIENT_URL = "https://localhost/api/v1"


def resource(items=()):
    def initialize(self):
        self._info["id"] = self._id
        self._info.update(items)

    return patch.object(Resource, "_initialize", new=initialize)


@pytest.fixture
def client() -> Client:
    return Client(CLIENT_URL, http_token="mysecret")
