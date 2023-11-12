#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pytest

""" tests related to classes in `zammadoo.resource` that can be performed offline """


def test_client_resources_are_singletons(client):
    tickets_1 = client.tickets
    tickets_2 = client.tickets
    assert tickets_1 is tickets_2


def test_resource_creation_with_info_needs_proper_id(client):
    with pytest.raises(AssertionError, match="must contain 'id'"):
        _ = client.tickets(1, info={"noid": True})

    with pytest.raises(AssertionError, match="be equal with rid"):
        _ = client.tickets(1, info={"id": 2})


def test_items_are_readonly(client):
    tickets = client.tickets

    with pytest.raises(TypeError):
        tickets(1, info={"id": 1})["id"] = tickets(2, info={"id": 2})["id"]


def test_representation_of_client(client_url, client):
    assert repr(client) == f"<Client '{client_url}'>"


def test_representation_of_client_resources(client_url, client):
    assert repr(client.users) == f"<Users '{client_url}/users'>"


def test_representation_of_client_resource(client_url, client):
    assert repr(client.tickets(34)) == f"<Ticket '{client_url}/tickets/34'>"


def test_resource_equality(client):
    tickets = client.tickets
    orphan_ticket = tickets._RESOURCE_TYPE(tickets, 123)
    client_ticket = tickets(123)

    assert client_ticket is not orphan_ticket
    assert client_ticket == orphan_ticket


def test_resource_of_different_class_are_not_equal(client):
    assert client.tickets(123) != client.users(123)


def test_resource_view_is_readonly(client):
    from collections.abc import Mapping

    view = client.tickets(123, info={"id": 123}).view()
    assert isinstance(view, Mapping)

    with pytest.raises(TypeError, match="does not support item assignment"):
        view["id"] = 123


@pytest.fixture(scope="function")
def ticket_with_set_cache(client):
    tickets = client.tickets
    cache = tickets.cache
    ticket = tickets(123)
    key = ticket.url
    assert key not in cache

    cache[key] = {"id": 123, "title": "some title"}
    return ticket


def test_lazy_object_on_getattr(ticket_with_set_cache):
    assert ticket_with_set_cache.title == "some title"


def test_lazy_object_on_getitem(ticket_with_set_cache):
    assert ticket_with_set_cache["title"] == "some title"


def test_lazy_object_on_view(ticket_with_set_cache):
    assert dict(ticket_with_set_cache.view()) == {"id": 123, "title": "some title"}
