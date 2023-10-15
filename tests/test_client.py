#!/usr/bin/env python
# -*- coding: UTF-8 -*-


def test_server_version(rclient):
    version = rclient.server_version.split(".")
    assert version[:2] == ["6", "1"]
