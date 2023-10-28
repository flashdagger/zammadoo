#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from . import assert_existing_tags


def test_representation_of_tags(client_url, client):
    assert repr(client.tags) == f"<Tags '{client_url}/tag_list'>"


def test_tags_getitem(rclient, assert_existing_tags):
    with assert_existing_tags("footag", "baztag"):
        assert "footag" in rclient.tags
        assert "baztag" in rclient.tags


def test_tag_search(rclient, assert_existing_tags):
    with assert_existing_tags("footag", "baztag"):
        found = rclient.tags.search("tag")
        assert {"footag", "baztag"}.issubset(found)


def test_tag_iteration(rclient, assert_existing_tags):
    tag_names = set()
    with assert_existing_tags("footag", "baztag"):
        for tag in rclient.tags:
            assert tag.keys() == {"name", "id", "count"}
            tag_names.add(tag["name"])

    assert {"footag", "baztag"}.issubset(tag_names)


def test_create_tag(rclient, assert_existing_tags):
    tag_name = "__pytest__"
    tags = rclient.tags

    with assert_existing_tags(delete={tag_name}):
        rclient.tags.create(tag_name)
        assert tag_name in tags
        tag_info = tags[tag_name]
        assert tag_info["name"] == tag_name
        assert tag_info["count"] == 0


def test_rename_tag(rclient, assert_existing_tags):
    tag_name = "__pytest__"
    new_tag_name = "__pytest_new__"
    tags = rclient.tags

    with assert_existing_tags(tag_name, delete={new_tag_name}):
        tag_info = tags[tag_name]
        tags.cache.clear()
        tags.rename(tag_name, new_tag_name)
        new_tag_info = tags[new_tag_name]
        assert new_tag_info["id"] == tag_info["id"]


def test_delete_tag(rclient, assert_existing_tags):
    tag_name = "__pytest__"
    tags = rclient.tags

    with assert_existing_tags(tag_name):
        tags.delete(tag_name)
        assert tag_name not in tags
