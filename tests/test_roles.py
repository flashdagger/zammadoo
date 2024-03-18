#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pytest


@pytest.mark.no_record
def test_roles_create_but_cannot_delete(rclient):
    """
    to delete the created role via the rails console use:

        sudo zammad run rails r "Role.find_by(name: 'Clone: Customer').destroy"

    """
    role = rclient.roles(3)
    assert role.name == "Customer"

    properties = dict(role.view())
    properties["name"] = "Clone: Customer"
    new_role = rclient.roles.create(**properties)

    with pytest.raises(NotImplementedError, match="roles cannot be deletet"):
        new_role.delete()


@pytest.mark.no_record
def test_role_update(rclient):
    """update the id to the newly created role"""
    role = rclient.roles(9)
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


def test_role_permission_caching(caplog, rclient):
    import logging

    api_url = rclient.url

    with caplog.at_level(logging.INFO, logger="zammadoo"):
        permissions_a = rclient.roles(1).permissions
        permissions_b = rclient.roles(1).permissions
        assert permissions_a == permissions_b

    # expect only one request with expand=true
    assert caplog.record_tuples == [
        ("zammadoo", logging.INFO, f"HTTP:GET {api_url}/roles/1?expand=true"),
    ]
