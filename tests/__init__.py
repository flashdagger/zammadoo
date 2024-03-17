#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from contextlib import contextmanager
from typing import Generator, Tuple

import pytest

from zammadoo.tickets import Ticket


@pytest.fixture(scope="function")
def single_ticket(rclient, temporary_resources) -> Generator[Ticket, None, None]:
    tickets = [
        {
            "title": "__pytest__",
            "customer_id": "guess:pytest@localhost.local",
            "group": "Users",
            "article": {"body": "..."},
        },
    ]

    with temporary_resources("tickets", *tickets) as infos:
        info = infos[0]
        yield rclient.tickets(info["id"], info=info)


@pytest.fixture(scope="function")
def ticket_pair(
    rclient, temporary_resources
) -> Generator[Tuple[Ticket, Ticket], None, None]:
    tickets = [
        {
            "title": "__pytest__",
            "customer_id": "guess:pytest@localhost.local",
            "group": "Users",
            "article": {"body": "..."},
        },
        {
            "title": "__pytest__",
            "customer_id": "guess:pytest@localhost.local",
            "group": "Users",
            "article": {"body": "..."},
        },
    ]

    with temporary_resources("tickets", *tickets) as infos:
        yield tuple(rclient.tickets(info["id"], info=info) for info in infos)


@pytest.fixture(scope="function")
def assert_existing_tags(zammad_api):
    def _cleanup(_tags):
        for tag_name in _tags:
            tag_infos = zammad_api("GET", f"tag_search?term={tag_name}").json()
            for info in tag_infos:
                if info["value"] == tag_name:
                    zammad_api("DELETE", f"tag_list/{info['id']}")

    @contextmanager
    def _create_temporary(*names, delete=()):
        temporary_tags = set(delete)
        _cleanup(temporary_tags)

        for tag_name in names:
            if tag_name not in temporary_tags:
                zammad_api("POST", "tag_list", {"name": tag_name})
                temporary_tags.add(tag_name)

        yield

        _cleanup(temporary_tags)

    return _create_temporary
