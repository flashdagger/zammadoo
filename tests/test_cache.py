#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
from itertools import zip_longest
from operator import eq

import pytest

from zammadoo.cache import LruCache


def fill_by_setitem(cache: LruCache, rng: range):
    for item in rng:
        cache[item] = item


def test_order_with_setitem():
    cache = LruCache()
    rng = range(1000)

    fill_by_setitem(cache, rng)
    assert len(rng) == len(cache)
    assert all(
        eq(a, b) for a, b in zip_longest(cache.keys(), cache.values())
    ), "key/value mismatch"
    assert all(eq(a, b) for a, b in cache.items()), "key/value mismatch"
    assert all(eq(a, b) for a, b in zip_longest(rng, cache.keys())), "data/key mismatch"


# def test_order_with_callback():
#     cache = LruCache()
#     rng = range(1000)
#
#     fill_by_callback(cache, rng)
#     assert len(rng) == len(cache)
#     assert all(
#         eq(a, b) for a, b in zip_longest(cache.keys(), cache.values())
#     ), "key/value mismatch"
#     assert all(eq(a, b) for a, b in zip_longest(rng, cache.keys())), "key/data mismatch"


def test_setitem_with_max_size_5():
    cache = LruCache(max_size=5)
    for item in range(15):
        cache[item] = item
        assert len(cache) == min(item + 1, 5)

    assert list(cache.keys()) == list(cache.values()) == [10, 11, 12, 13, 14]


def test_setitem_with_max_size_0():
    cache = LruCache(max_size=0)
    for item in range(10):
        cache[item] = item
        assert len(cache) == 0

    cache.evict()
    assert len(cache) == 0


def test_setdefault_with_max_size_0():
    cache = LruCache(max_size=0)
    assert cache.setdefault(0, 0) == 0
    assert len(cache) == 0


def test_setdefault_with_max_size_5():
    cache = LruCache(max_size=5)
    for item in range(15):
        cache.setdefault(item, item)
        assert len(cache) == min(item + 1, 5)

    assert list(cache.keys()) == list(cache.values()) == [10, 11, 12, 13, 14]


def test_setitem_overwrites_value():
    cache = LruCache()
    cache["foo"] = "bar"
    assert cache["foo"] == "bar"
    cache["foo"] = "baz"
    assert cache["foo"] == "baz"


def test_setdefault_does_not_overwrites_value():
    cache = LruCache()
    cache.setdefault("foo", "bar")
    assert cache["foo"] == "bar"
    cache.setdefault("foo", "baz")
    assert cache["foo"] == "bar"


def test_setdefault_makes_existing_item_most_recent_if_max_size_greater_1():
    cache = LruCache(2)
    cache.setdefault(0, 0)
    cache.setdefault(1, 1)
    assert tuple(cache.keys())[-1] == 1
    cache.setdefault(0, 0)
    assert tuple(cache.keys())[-1] == 0


def test_setitem_makes_existing_item_most_recent_if_max_size_greater_1():
    cache = LruCache(2)
    cache[0] = 0
    cache[1] = 1
    assert tuple(cache.keys())[-1] == 1
    cache[0] = 0
    assert tuple(cache.keys())[-1] == 0


def test_getitem_makes_existing_item_most_recent_if_max_size_greater_1():
    cache = LruCache(2)
    cache[0] = 0
    cache[1] = 1
    assert tuple(cache.keys())[-1] == 1
    _ = cache[0]
    assert tuple(cache.keys())[-1] == 0


def test_with_max_size_1():
    cache = LruCache(1)
    cache[0] = 0
    assert cache[0] == 0
    cache[1] = 1
    assert cache[1] == 1
    cache.setdefault(2, 2)
    assert cache[2] == 2
    with pytest.raises(KeyError):
        _ = cache[1]


def test_reducing_max_size_evicts_older_entries():
    cache = LruCache(max_size=20)
    fill_by_setitem(cache, range(20))
    assert len(cache) == 20
    cache.max_size -= 15
    assert len(cache) == 5
    assert list(cache.keys()) == [15, 16, 17, 18, 19]


def test_delitem():
    cache = LruCache(max_size=10)
    rng = range(10)
    fill_by_setitem(cache, rng)
    assert 5 in cache
    del cache[5]
    assert len(cache) == 9
    assert 5 not in cache


def test_clear():
    cache = LruCache()
    fill_by_setitem(cache, range(20))
    assert bool(cache)
    cache.clear()
    assert 0 not in cache
    assert len(cache) == 0
    assert not cache


def test_age_s():
    cache = LruCache()
    assert cache.age_s("foo") is None

    cache["foo"] = "bar"
    start = time.monotonic()
    while time.monotonic() - start < 0.015:
        time.sleep(0.001)
    assert 0.0145 < cache.age_s("foo") < 0.0165

    cache["foo"] = "baz"
    assert cache.age_s("foo") < 0.001


def test_evict_by_age():
    cache = LruCache()
    cache["first"] = None
    time.sleep(0.015)
    cache["second"] = None

    cache.evict()
    assert cache.keys() == {"first", "second"}

    cache.evict(max_age_s=0.0145)
    assert cache.keys() == {"second"}
