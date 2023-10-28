#!/usr/bin/env python
# -*- coding: UTF-8 -*-


def test_create_organization(rclient, temporary_resources):
    with temporary_resources("organizations") as organizations:
        new_organization = rclient.organizations.create("pytest_organization")
        organizations.append(new_organization.view())
        assert new_organization.active is True
        assert new_organization.domain == ""
        assert new_organization.domain_assignment is False
        assert new_organization.note == ""
        assert new_organization.shared is True


def test_organization_members_attribute(client):
    organization = client.organizations(
        1, info={"id": 1, "member_ids": [1, 2, 3], "secondary_member_ids": [4, 5]}
    )
    users = client.users
    assert organization.members == [users(1), users(2), users(3)]
    assert organization.secondary_members == [users(4), users(5)]
