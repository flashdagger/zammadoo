#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime

import pytest

""" tests related to Resource subclass attributes that can be performed offline """


def test_missing_attributes(client):
    with pytest.raises(AttributeError, match="has no attribute"):
        _ = client.tickets(1, info={"id": 1}).missing


def test_attributes_are_readonly(client):
    tickets = client.tickets

    with pytest.raises(AttributeError, match="is read-only"):
        tickets(1, info={"id": 1, "title": "some title"}).title = "other title"


def test_id_attribute(client):
    assert client.tickets(123).id == 123


def test_datetime_type_attribute(client):
    ticket = client.tickets(1, info={"id": 1, "created_at": "2021-11-03T11:51:13.759Z"})

    created_at = ticket.created_at
    assert isinstance(created_at, datetime)
    assert created_at.tzname() == "UTC"


def test_user_last_login_is_datetime(client):
    assert isinstance(
        client.users(
            1, info={"id": 1, "last_login": "2021-11-03T11:51:13.759Z"}
        ).last_login,
        datetime,
    )


def test_user_last_login_is_none(client):
    assert client.users(1, info={"id": 1, "last_login": None}).last_login is None


def test_access_item_named_from(client):
    # 'from' is a reserved word in python
    assert (
        client.users(1, info={"id": 1, "from": "user@example.com"}).from_
        == "user@example.com"
    )


def test_name_attribute(client):
    group = client.groups(123, info={"id": 123, "name": "Users"})
    assert group.name == "Users"


def test_users_attribute(client):
    group = client.groups(123, info={"id": 123, "user_ids": [1, 2, 3]})
    users = client.users
    assert group.users == [users(1), users(2), users(3)]


def test_members_attribute(client):
    organization = client.organizations(123, info={"id": 123, "member_ids": [1, 2, 3]})
    users = client.users
    assert organization.members == [users(1), users(2), users(3)]


def test_groups_attribute(client):
    role = client.roles(123, info={"id": 123, "group_ids": [1, 2, 3]})
    groups = client.groups
    assert role.groups == [groups(1), groups(2), groups(3)]


def test_updated_by_attribute(client):
    ticket = client.tickets(123, info={"id": 123, "updated_by_id": 456})
    assert ticket.updated_by == client.users(456)


def test_resources_url_attribute(client):
    assert client.tickets.url == f"{client.url}/tickets"


def test_resource_url_attribute(client):
    assert client.tickets(12345).url == f"{client.url}/tickets/12345"


def test_organization_weburl_attribute(client):
    organization = client.organizations(12345)
    assert organization.weburl == f"{client.weburl}/#organization/profile/12345"
