#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from datetime import datetime

import pytest

from . import single_ticket


def test_create_ticket_time_accounting_default_type(single_ticket):
    accounting = single_ticket.create_time_accounting(12.3)

    assert accounting.time_unit == "12.3"
    assert accounting.type is None
    assert (
        accounting.created_by
        == accounting.updated_by
        == single_ticket.parent.client.users.me()
    )
    assert accounting.ticket == single_ticket
    assert accounting.ticket_article is None

    single_ticket.reload()
    assert single_ticket.time_accountings() == [accounting]
    assert single_ticket.time_unit == "12.3"

    accounting.delete()
    single_ticket.reload()
    assert single_ticket.time_accountings() == []
    assert single_ticket.time_unit == "0.0"


def test_create_ticket_time_accounting_with_type(single_ticket):
    client = single_ticket.parent.client
    accounting_type = next(iter(client.time_accountings.types))

    accounting = single_ticket.create_time_accounting("1.0", type_id=accounting_type.id)
    assert accounting.time_unit == "1.0"
    assert accounting.type == accounting_type

    accounting = single_ticket.create_time_accounting("1.1", type=accounting_type.name)
    assert accounting.time_unit == "1.1"
    assert accounting.type == accounting_type

    accounting = single_ticket.create_time_accounting("1.2", type=accounting_type)
    assert accounting.time_unit == "1.2"
    assert accounting.type == accounting_type


def test_create_time_accounting_types(rclient):
    from zammadoo.users import User

    type_name = "__pytest"
    atypes = rclient.time_accountings.types
    atype = atypes.create(type_name)
    assert atype.active  # default
    assert atype.note is None  # default
    assert isinstance(atype.url, str)
    assert isinstance(atype.created_by, User)
    assert isinstance(atype.created_at, datetime)
    assert atype in list(atypes)

    # test cached info for newly created instances
    assert atype.view() == atypes(atype.id).view()
    atypes.cache.clear()
    # test cached info for newly created instances if cache is empty
    assert atype.view() == atypes(atype.id).view()

    assert atype.name == type_name
    with pytest.raises(NotImplementedError):
        atype.delete()
