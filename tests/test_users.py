#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from datetime import datetime


def test_user_name_attribute(client):
    user = client.users(123, info={"id": 123, "login": "someone@pytest"})
    assert user.name == "someone@pytest"


def test_user_fullname_attribute_given_firstname_only(client):
    user = client.users(123, info={"id": 123, "firstname": "Max", "lastname": None})
    assert user.fullname == user.firstname == "Max"


def test_user_fullname_attribute_given_lastname_only(client):
    user = client.users(
        123, info={"id": 123, "firstname": None, "lastname": "Headroom"}
    )
    assert user.fullname == user.lastname == "Headroom"


def test_user_fullname_attribute_given_firstname_and_lastname(client):
    user = client.users(
        123, info={"id": 123, "firstname": "Max", "lastname": "Headroom"}
    )
    assert user.fullname == "Max Headroom"


def test_user_groups_attribute(client):
    user = client.users(123, info={"id": 123, "group_ids": [1, 2, 3]})
    groups = client.groups
    assert user.groups == [groups(1), groups(2), groups(3)]


def test_user_last_login_is_datetime(client):
    assert isinstance(
        client.users(
            1, info={"id": 1, "last_login": "2021-11-03T11:51:13.759Z"}
        ).last_login,
        datetime,
    )


def test_user_last_login_is_none(client):
    assert client.users(1, info={"id": 1, "last_login": None}).last_login is None


def test_user_organization_attribute(client):
    user = client.users(123, info={"id": 123, "organization_id": 45})
    assert user.organization == client.organizations(45)


def test_user_organizations_attribute(client):
    user = client.users(123, info={"id": 123, "organization_ids": [1, 2, 3]})
    organizations = client.organizations
    assert user.organizations == [organizations(1), organizations(2), organizations(3)]


def test_user_role_attribute(client):
    user = client.users(123, info={"id": 123, "role_ids": [1, 2, 3]})
    roles = client.roles
    assert user.roles == [roles(1), roles(2), roles(3)]


def test_user_weburl_attribute(client):
    user = client.users(123)
    assert user.weburl == f"{client.weburl}/#user/profile/123"


def test_create_user(rclient, temporary_resources):
    from uuid import UUID

    with temporary_resources("users") as users:
        new_user = rclient.users.create(firstname="John", lastname="Pytest")
        users.append(new_user.view())

    assert new_user.active is True
    assert new_user.fullname == "John Pytest"
    assert new_user.note == ""

    assert new_user.login.startswith("auto-")
    uuid = UUID(new_user.login[5:])
    assert uuid.version == 4
