#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import pytest


def test_roles_create_but_cannot_delete(rclient):
    role = rclient.roles(3)
    assert role.name == "Customer"

    properties = dict(role.view())
    properties["name"] = "Clone: Customer"
    new_role = rclient.roles.create(**properties)

    with pytest.raises(NotImplementedError, match="roles cannot be deletet"):
        new_role.delete()


def test_role_update(rclient):
    role = rclient.roles(7)
    assert role.name == "Clone: Customer"
    updated_role = role.update(active=False)
    assert updated_role.active is False