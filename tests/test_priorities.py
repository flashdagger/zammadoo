#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pytest


def test_create_priority(rclient, temporary_resources):
    with temporary_resources("ticket_priorities") as priorities:
        new_priority = rclient.ticket_priorities.create("pytest_priority")
        priorities.append(new_priority.view())
        assert new_priority.active is True
        assert new_priority.note is None
        assert new_priority.default_create is False
        assert new_priority.ui_icon is None
        assert new_priority.ui_color is None


def test_update_priority(rclient, temporary_resources):
    with temporary_resources("ticket_priorities", {"name": "pytest_priority"}) as infos:
        info = infos[0]
        priority = rclient.ticket_priorities(info["id"], info=info)
        assert priority.active is True
        updated_priority = priority.update(active=False)
        assert updated_priority.active is False


def test_update_priority_with_reload(rclient, temporary_resources):
    with temporary_resources("ticket_priorities", {"name": "pytest_priority"}) as infos:
        info = infos[0]
        priority = rclient.ticket_priorities(info["id"], info=info)
        assert priority.active is True
        priority.update(active=False)
        priority.reload()
        assert priority.active is False


def test_delete_priority(rclient, temporary_resources):
    from zammadoo import APIException

    with temporary_resources("ticket_priorities", {"name": "pytest_priority"}) as infos:
        info = infos[0]
        priority = rclient.ticket_priorities(info["id"], info=info)
        priority.delete()
        with pytest.raises(APIException, match="Couldn't find Ticket::Priority"):
            priority.reload()
        infos.clear()
