from timeit import timeit

import pytest

from zammadoo import Client
from zammadoo.tickets import Ticket
from zammadoo.users import User

number = int(1e5)


@pytest.fixture(scope="module")
def info_ticket() -> Ticket:
    client = Client("https://localhost/api/v1", http_token="myfaketoken")
    info = {"id": 123, "title": "some title", "created_at": "2024-03-18T22:43:07.089Z"}
    return client.tickets(123, info=info)


@pytest.fixture(scope="module")
def info_user() -> User:
    client = Client("https://localhost/api/v1", http_token="myfaketoken")
    info = {"id": 123, "login": "john.doe@pytest"}
    return client.users(123, info=info)


def test_info_attribute(info_ticket, benchmark):
    benchmark(timeit, "ticket.id", number=number, globals={"ticket": info_ticket})


def test_info_getattr(info_ticket, benchmark):
    benchmark(timeit, "ticket.title", number=number, globals={"ticket": info_ticket})


def test_info_getitem(info_ticket, benchmark):
    benchmark(timeit, "ticket['title']", number=number, globals={"ticket": info_ticket})


def test_info_datetime(info_ticket, benchmark):
    benchmark(
        timeit, "ticket.created_at", number=number, globals={"ticket": info_ticket}
    )


def test_info_descriptor(info_user, benchmark):
    benchmark(timeit, "user.name", number=number, globals={"user": info_user})
