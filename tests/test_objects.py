#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from datetime import datetime
from unittest.mock import patch

import pytest

from zammadoo import Client
from zammadoo.resource import Resource


def mocked_resource(items=()):
    def mocked_initialize(self):
        self._info["id"] = self._id
        self._info.update(items)

    return patch.object(Resource, "_initialize", new=mocked_initialize)


@pytest.fixture
def client() -> Client:
    return Client("/", http_token="mysecret")


def test_client_resources_are_singletons(client):
    tickets_1 = client.tickets
    tickets_2 = client.tickets
    assert tickets_1 is tickets_2


def test_client_resource_are_cached_if_referenced(client):
    tickets1_1 = client.tickets(1)
    tickets1_2 = client.tickets(1)

    assert tickets1_1 is tickets1_2

    del tickets1_1
    tickets1_3 = client.tickets(1)

    assert tickets1_2 is tickets1_3


@mocked_resource()
def test_missing_attributes(client):
    with pytest.raises(AttributeError, match="has no attribute"):
        _ = client.tickets(1).missing


@mocked_resource({"title": "some title"})
def test_attributes_are_readonly(client):
    tickets = client.tickets

    with pytest.raises(AttributeError, match="is read-only"):
        tickets(1).title = tickets(2).title


@mocked_resource()
def test_items_are_readonly(client):
    tickets = client.tickets

    with pytest.raises(TypeError):
        tickets(1)["id"] = tickets(2)["id"]


@mocked_resource({"created_at": "2021-11-03T11:51:13.759Z"})
def test_datetime_attribute(client):
    ticket = client.tickets(1)

    created_at = ticket.created_at
    assert isinstance(created_at, datetime)
    assert created_at.tzname() == "UTC"


@mocked_resource({"last_login": "2021-11-03T11:51:13.759Z"})
def test_user_last_login_is_datetime(client):
    assert isinstance(client.users(1).last_login, datetime)


@mocked_resource({"last_login": None})
def test_user_last_login_is_none(client):
    assert client.users(1).last_login is None
