#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from sys import getrefcount
from weakref import getweakrefcount, ref

import pytest

from .mocked import CLIENT_URL, client, resource


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


def test_client_resource_instance_has_weak_reference(client):
    tickets1_1 = client.tickets(1)
    assert getrefcount(tickets1_1) == 2
    assert getweakrefcount(tickets1_1) == 1

    tickets1_2 = client.tickets(1)
    assert getrefcount(tickets1_2) == 3
    assert getweakrefcount(tickets1_2) == 1

    del tickets1_2
    assert getrefcount(tickets1_1) == 2
    assert getweakrefcount(tickets1_1) == 1

    tickets1_1_wref = ref(tickets1_1)
    assert getrefcount(tickets1_1) == 2
    assert getweakrefcount(tickets1_1) == 2

    del tickets1_1
    assert tickets1_1_wref() is None


@resource()
def test_missing_attributes(client):
    with pytest.raises(AttributeError, match="has no attribute"):
        _ = client.tickets(1).missing


@resource({"title": "some title"})
def test_attributes_are_readonly(client):
    tickets = client.tickets

    with pytest.raises(AttributeError, match="is read-only"):
        tickets(1).title = tickets(2).title


@resource()
def test_items_are_readonly(client):
    tickets = client.tickets

    with pytest.raises(TypeError):
        tickets(1)["id"] = tickets(2)["id"]


def test_representation_of_client(client):
    assert repr(client) == f"<Client '{CLIENT_URL}'>"


def test_representation_of_client_resources(client):
    assert repr(client.users) == f"<Users '{CLIENT_URL}/users'>"


def test_representation_of_client_resource(client):
    assert repr(client.tickets(34)) == f"<Ticket '{CLIENT_URL}/tickets/34'>"


@resource({"created_at": "2021-11-03T11:51:13.759Z"})
def test_datetime_attribute(client):
    ticket = client.tickets(1)

    created_at = ticket.created_at
    assert isinstance(created_at, datetime)
    assert created_at.tzname() == "UTC"


@resource({"last_login": "2021-11-03T11:51:13.759Z"})
def test_user_last_login_is_datetime(client):
    assert isinstance(client.users(1).last_login, datetime)


@resource({"last_login": None})
def test_user_last_login_is_none(client):
    assert client.users(1).last_login is None


@resource({"from": "user@example.com"})
def test_access_item_named_from(client):
    # 'from' is a reserved word in python
    assert client.users(1).from_ == "user@example.com"


def test_resources_url(client):
    assert client.tickets.url == f"{client.url}/tickets"


def test_resource_url(client):
    assert client.tickets(12345).url == f"{client.url}/tickets/12345"
