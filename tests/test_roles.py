#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import pytest


@pytest.mark.no_record
def test_roles_create_but_cannot_delete(rclient):
    role = rclient.roles(3)
    assert role.name == "Customer"

    properties = dict(role.view())
    properties["name"] = "Clone: Customer"
    new_role = rclient.roles.create(**properties)

    with pytest.raises(NotImplementedError, match="roles cannot be deletet"):
        new_role.delete()


@pytest.mark.no_record
def test_role_update(rclient):
    role = rclient.roles(7)
    assert role.name == "Clone: Customer"
    updated_role = role.update(active=False)
    assert updated_role.active is False


def test_role_iteration(rclient):
    roles = tuple(rclient.roles)
    assert len(roles) > 2
    assert tuple(rclient.roles.iter(page=None, per_page=1)) == roles


def test_role_permission_attribute(rclient):
    role = rclient.roles(1)
    assert role.name == "Admin"
    assert role.permissions == [
        "admin",
        "user_preferences",
        "report",
        "knowledge_base.editor",
    ]
