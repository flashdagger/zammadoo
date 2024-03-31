#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging


def test_notifications_iter(caplog, rclient):
    api_url = rclient.url

    with caplog.at_level(logging.INFO, logger="zammadoo"):
        # parameters are ignored
        notifications = list(rclient.notificatons.iter(page=10, expand=False))

    # expect only one request without expand
    assert caplog.record_tuples == [
        (
            "zammadoo",
            logging.INFO,
            f"HTTP:GET {api_url}/online_notifications?expand=true",
        ),
    ]


def test_mark_all_as_read(caplog, rclient):
    api_url = rclient.url

    with caplog.at_level(logging.INFO, logger="zammadoo"):
        rclient.notificatons.mark_all_as_read()

    assert caplog.record_tuples == [
        (
            "zammadoo",
            logging.INFO,
            f"HTTP:POST {api_url}/online_notifications/mark_all_as_read",
        ),
    ]


def test_always_use_expand_true(caplog, rclient):
    api_url = rclient.url

    with caplog.at_level(logging.INFO, logger="zammadoo"):
        _ = rclient.notificatons(263).seen
        rclient.notificatons(263).reload()

    assert caplog.record_tuples == 2 * [
        (
            "zammadoo",
            logging.INFO,
            f"HTTP:GET {api_url}/online_notifications/263?expand=true",
        ),
    ]
