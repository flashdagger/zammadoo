#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pytest


def test_create_state(rclient, temporary_resources):
    with temporary_resources("ticket_states") as states:
        new_state = rclient.ticket_states.create("pytest_state", state_type_id=5)
        states.append(new_state.view())
        assert new_state.active is True
        assert new_state.note is None
        assert new_state.next_state is None
        assert new_state.state_type_id == 5
        assert new_state.ignore_escalation is False
        assert new_state.default_create is False
        assert new_state.default_follow_up is False


def test_update_state(rclient, temporary_resources):
    with temporary_resources(
        "ticket_states", {"name": "pytest_state", "state_type_id": 1}
    ) as infos:
        info = infos[0]
        state = rclient.ticket_states(info["id"], info=info)
        assert state.active is True
        updated_state = state.update(active=False)
        assert updated_state.active is False


def test_update_state_with_reload(rclient, temporary_resources):
    with temporary_resources(
        "ticket_states", {"name": "pytest_state", "state_type_id": 1}
    ) as infos:
        info = infos[0]
        state = rclient.ticket_states(info["id"], info=info)
        assert state.active is True
        state.update(active=False)
        state.reload()
        assert state.active is False


def test_delete_state(rclient, temporary_resources):
    from zammadoo import APIException

    with temporary_resources(
        "ticket_states", {"name": "pytest_state", "state_type_id": 1}
    ) as infos:
        info = infos[0]
        state = rclient.ticket_states(info["id"], info=info)
        state.delete()
        with pytest.raises(APIException, match="Couldn't find Ticket::State"):
            state.reload()
        infos.clear()


def test_state_state_type_attribute(client):
    state = client.ticket_states(1, info={"id": 1, "state_type_id": 1})
    assert state.state_type_id == 1


def test_state_next_state_attribute_is_not_none(client):
    state = client.ticket_states(1, info={"id": 1, "next_state_id": 2})
    assert state.next_state == client.ticket_states(2)


def test_state_next_state_attribute_is_none(client):
    state = client.ticket_states(1, info={"id": 1, "next_state_id": None})
    assert state.next_state is None
