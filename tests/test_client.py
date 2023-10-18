#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pytest

from zammadoo import APIException


def test_server_version(rclient):
    version = rclient.server_version.split(".")
    assert version[:2] == ["6", "1"]


def test_raise_if_user_cannot_be_found(rclient):
    with pytest.raises(APIException, match="Couldn't find User") as exc:
        rclient.users(100).reload()

    assert exc.value.response.status_code == 404
