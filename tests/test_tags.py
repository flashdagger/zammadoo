#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from contextlib import suppress

import pytest

from zammadoo.utils import TypedTag


def test_representation_of_tags(request, client):
    client_url = request.config.getoption("--client-url")
    assert repr(client.tags) == f"<Tags '{client_url}/tag_list'>"


def test_tag_iteration(rclient):
    for tag in rclient.tags:
        assert tag.keys() == {"name", "id", "count"}
        break


def test_mutable_tag_operations(rclient):
    tag_name = "__pytest__"
    new_tag_name = "__pytest_new__"
    tags = rclient.tags

    # make sure tag does not exist
    with suppress(KeyError):
        tags.delete(tag_name)
    with suppress(KeyError):
        tags.delete(new_tag_name)

    assert tag_name not in tags

    with pytest.raises(KeyError, match=tag_name):
        tags.delete(tag_name)

    tags.create(tag_name)
    assert tag_name in tags
    tag_info = tags[tag_name]
    assert tag_info["name"] == tag_name
    assert tag_info["count"] == 0

    assert tag_name in tags.search(tag_name)

    tags.cache.clear()
    tags.rename(tag_name, new_tag_name)
    assert new_tag_name in tags
    assert tag_name not in tags

    tags.cache.clear()
    assert tag_info["id"] == tags[new_tag_name]["id"]

    tags.delete(new_tag_name)
