#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from unittest.mock import patch

import pytest

from zammadoo import Client
from zammadoo.resource import Resource


def mocked_initialize(self):
    self._info["id"] = self._id


@pytest.fixture
def client():
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


def test_attributes_are_readonly(client):
    tickets = client.tickets

    with pytest.raises(AttributeError):
        tickets(1).id = tickets(2).id

    with pytest.raises(AttributeError):
        del tickets(1).id


@patch.object(Resource, "_initialize", new=mocked_initialize)
def test_item_are_readonly(client):
    tickets = client.tickets

    with pytest.raises(TypeError):
        tickets(1)["id"] = tickets(2)["id"]
