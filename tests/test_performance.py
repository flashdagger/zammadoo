#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timezone
from timeit import timeit

import pytest

from zammadoo import Client
from zammadoo.tickets import Ticket
from zammadoo.users import User

TEST_COUNT = int(1e5)


@pytest.fixture(scope="module")
def info_ticket() -> Ticket:
    client = Client("https://localhost/api/v1", http_token="myfaketoken")
    info = {"id": 123, "title": "some title", "created_at": "2024-03-18T22:43:07.089Z"}
    yield client.tickets(123, info=info)


@pytest.fixture(scope="module")
def info_user() -> User:
    def _myprop(self):
        return self["login"]

    client = Client("https://localhost/api/v1", http_token="myfaketoken")
    info = {"id": 123, "login": "john.doe@pytest"}
    user = client.users(123, info=info)
    user.__class__.property = property(_myprop)
    yield user


def test_info_attribute(info_ticket, benchmark):
    assert info_ticket.id == 123
    benchmark(timeit, "ticket.id", number=TEST_COUNT, globals={"ticket": info_ticket})


def test_info_getattr(info_ticket, benchmark):
    assert info_ticket.title == "some title"
    benchmark(
        timeit, "ticket.title", number=TEST_COUNT, globals={"ticket": info_ticket}
    )


def test_info_getitem(info_ticket, benchmark):
    assert info_ticket["title"] == "some title"
    benchmark(
        timeit, "ticket['title']", number=TEST_COUNT, globals={"ticket": info_ticket}
    )


def test_info_datetime(info_ticket, benchmark):
    assert info_ticket.created_at == datetime(
        2024,
        3,
        18,
        22,
        43,
        7,
        89000,
        timezone.utc,
    )
    benchmark(
        timeit, "ticket.created_at", number=TEST_COUNT, globals={"ticket": info_ticket}
    )


def test_info_descriptor(info_user, benchmark):
    assert info_user.name == "john.doe@pytest"
    benchmark(timeit, "user.name", number=TEST_COUNT, globals={"user": info_user})


def test_info_property(info_user, benchmark):
    assert info_user.property == "john.doe@pytest"
    benchmark(timeit, "user.property", number=TEST_COUNT, globals={"user": info_user})


def test_parent_client(info_user, benchmark):
    assert info_user.parent.client is not None
    benchmark(
        timeit, "user.parent.client", number=TEST_COUNT, globals={"user": info_user}
    )
