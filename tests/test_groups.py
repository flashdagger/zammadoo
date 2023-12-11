#!/usr/bin/env python
# -*- coding: UTF-8 -*-


def test_create_group(rclient, temporary_resources):
    with temporary_resources("groups") as groups:
        new_group = rclient.groups.create("pytest_group")
        groups.append(new_group.view())
        assert new_group.active is True
        assert new_group.note is None
        assert new_group.parent_group is None


def test_group_users_attribute(client):
    group = client.groups(1, info={"id": 1, "user_ids": [1, 2, 3]})
    users = client.users
    assert group.users == [users(1), users(2), users(3)]
