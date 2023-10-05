#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pytest

from zammadoo import Client


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
