#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime

from . import ticket_pair


def test_ticket_time_accounting(ticket_pair):
    ticket_a, ticket_b = ticket_pair
    accountings = ticket_a.time_accountings
    assert not accountings

    client = ticket_a.parent.client
    accounting = client.time_accountings.create(12.3, ticket_a)

    assert accounting.time_unit == "12.3"
    assert accounting.type is None
    assert accounting.ticket == ticket_a
    assert accounting.created_by == accounting.updated_by == client.users.me()
    assert isinstance(accounting.created_at, datetime)
    assert accounting.created_at == accounting.updated_at
    assert accounting.ticket_article is None

    new_article = ticket_a.create_article(
        "article with added accounting", time_unit="4.5"
    )
    accountings = ticket_a.time_accountings
    assert len(accountings) == 2
    assert accountings[1].ticket_article == new_article

    accountings[1].delete()
    accountings = ticket_a.time_accountings
    assert len(accountings) == 1

    accounting_types = client.time_accountings.types()
    assert accounting_types
    type_name = accounting_types[0]["name"]
    type_id = accounting_types[0]["id"]

    new_accounting = accountings[0].update(type=type_name)
    assert new_accounting.type == type_name

    new_accounting = client.time_accountings.create(0, ticket_b, type_=type_name)
    assert new_accounting.type == type_name

    new_accounting = client.time_accountings.create(0, ticket_b, type_=type_id)
    assert new_accounting.type_id == type_id
