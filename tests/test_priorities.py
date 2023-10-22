#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from contextlib import contextmanager

import pytest


@pytest.fixture(scope="function")
def assert_existing_priorities(zammad_api):
    def _cleanup(names):
        priority_map = {}
        priority_map.update(
            (info["name"], info["id"])
            for info in zammad_api("GET", "ticket_priorities").json()
        )
        for name in names:
            priority_id = priority_map.get(name)
            if not priority_id:
                continue
            zammad_api("DELETE", f"ticket_priorities/{priority_id}")

    @contextmanager
    def _create_temporary(*names, delete=()):
        temporary_priorities = set(delete)
        _cleanup(temporary_priorities)

        for priority_name in names:
            if priority_name not in temporary_priorities:
                zammad_api(
                    "POST",
                    "ticket_priorities",
                    {"name": priority_name, "note": "pytest"},
                )
                temporary_priorities.add(priority_name)

        yield

        _cleanup(temporary_priorities)

    return _create_temporary


def test_create_and_update_priority(rclient, assert_existing_priorities):
    with assert_existing_priorities(delete={"pytest_prio"}):
        new_priority = rclient.ticket_priorities.create("pytest_prio")
        assert new_priority.active is True
        updated_priority = new_priority.update(active=False)
        assert updated_priority.active is False
