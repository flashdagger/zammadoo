#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" tests related to classes in `zammadoo.resource` that can be performed offline """

import pytest

from zammadoo.tickets import Ticket


def test_client_resources_are_singletons(client):
    tickets_1 = client.tickets
    tickets_2 = client.tickets
    assert tickets_1 is tickets_2


def test_resource_creation_with_info_needs_proper_id(client):
    with pytest.raises(AssertionError, match="must contain 'id'"):
        _ = client.tickets(1, info={"noid": True})

    with pytest.raises(AssertionError, match="equal to rid"):
        _ = client.tickets(1, info={"id": 2})


def test_items_are_readonly(client):
    ticket = client.tickets(1, info={"id": 1})

    with pytest.raises(TypeError):
        ticket["id"] = 2

    with pytest.raises(AttributeError, match="read-only"):
        ticket.title = ""

    with pytest.raises(AttributeError, match="read-only"):
        del ticket.title


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
def ticket_with_set_cache(client) -> Ticket:
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


def test_resource_info_is_copy(client):
    tickets = client.tickets
    tickets.cache.max_size = -1

    init_info = {"id": 123, "title": "other title"}
    ticket = tickets(123, info=init_info)

    ticket_info = ticket._info
    assert init_info == ticket_info
    assert init_info is not ticket_info

    cache_info = tickets.cache[ticket.url]
    assert init_info == cache_info
    assert cache_info is not ticket_info
    assert init_info is not cache_info


def test_resources_caching_enabled(client):
    tickets = client.tickets
    tickets.cache.max_size = -1

    info = {"id": 123, "title": "some title"}
    ticket = tickets(123, info=info)
    assert tickets.cache[ticket.url] == info
    assert dict(tickets(123).view()) == info


def test_resources_caching_disabled(client):
    tickets = client.tickets
    tickets.cache.max_size = 0

    info = {"id": 123, "title": "some title"}
    ticket = tickets(123, info=info)
    assert ticket.url not in tickets.cache
    assert not tickets.cache


def test_dir(client):
    tickets = client.tickets

    info = {"id": 123, "title": "some title"}
    ticket = tickets(123, info=info)

    assert "title" in dir(ticket)
