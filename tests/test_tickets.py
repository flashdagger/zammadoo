#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time

import pytest

from . import assert_existing_tags, single_ticket, ticket_pair


def test_ticket_customer_attribute(client):
    ticket = client.tickets(123, info={"id": 123, "customer_id": 456})
    assert ticket.customer == client.users(456)


def test_ticket_group_attribute(client):
    ticket = client.tickets(123, info={"id": 123, "group_id": 456})
    assert ticket.group == client.groups(456)


def test_ticket_organization_attribute(client):
    ticket = client.tickets(123, info={"id": 123, "organization_id": 456})
    assert ticket.organization == client.organizations(456)


def test_ticket_organization_attribute_is_none(client):
    ticket = client.tickets(123, info={"id": 123, "organization_id": None})
    assert ticket.organization is None


def test_ticket_owner_attribute(client):
    ticket = client.tickets(123, info={"id": 123, "owner_id": 456})
    assert ticket.owner == client.users(456)


def test_ticket_priority_attribute(client):
    ticket = client.tickets(123, info={"id": 123, "priority_id": 456})
    assert ticket.priority == client.ticket_priorities(456)


def test_ticket_state_attribute(client):
    ticket = client.tickets(123, info={"id": 123, "state_id": 456})
    assert ticket.state == client.ticket_states(456)


def test_ticket_weburl_attripute(client):
    ticket = client.tickets(123, info={"id": 123})
    assert ticket.weburl == f"{client.weburl}/#ticket/zoom/123"


def test_tickets_create_body_only(rclient, temporary_resources):
    with temporary_resources("tickets") as infos:
        ticket = rclient.tickets.create(
            "__pytest__",
            "Users",
            "guess:pytest@localhost.local",
            "article body",
        )
        infos.append(ticket.view())
        assert ticket.title == "__pytest__"
        assert ticket.group.name == "Users"
        assert ticket.customer.login == "pytest@localhost.local"
        assert ticket.organization is None
        assert ticket.owner.id == 1
        assert ticket.article_count == 1
        assert ticket.tags() == []
        assert ticket.links() == {"parent": [], "child": [], "normal": []}

        article = ticket.articles[0]
        assert article.body == "article body"
        assert article.internal is False


def test_tickets_create_with_article_params(rclient, temporary_resources):
    with temporary_resources("tickets") as infos:
        ticket = rclient.tickets.create(
            "__pytest__",
            "Users",
            "guess:pytest@localhost.local",
            {"body": "article body", "internal": True},
        )
        infos.append(ticket.view())
        article = ticket.articles[0]
        assert article.body == "article body"
        assert article.internal is True


def test_ticket_link_with_and_unlink__normal(ticket_pair):
    ticket_a, ticket_b = ticket_pair
    ticket_a.link_with(ticket_b)
    assert ticket_a.links() == {"parent": [], "child": [], "normal": [ticket_b]}
    assert ticket_b.links() == {"parent": [], "child": [], "normal": [ticket_a]}

    ticket_a.unlink_from(ticket_b, "normal")
    assert ticket_a.links() == {"parent": [], "child": [], "normal": []}
    assert ticket_b.links() == {"parent": [], "child": [], "normal": []}


def test_ticket_link_with_and_unlink_from__parent_child(ticket_pair):
    ticket_a, ticket_b = ticket_pair
    ticket_a.link_with(ticket_b, link_type="child")
    assert ticket_a.links() == {"parent": [], "child": [ticket_b], "normal": []}
    assert ticket_b.links() == {"parent": [ticket_a], "child": [], "normal": []}

    ticket_a.unlink_from(ticket_b)
    assert ticket_a.links() == {"parent": [], "child": [], "normal": []}
    assert ticket_b.links() == {"parent": [], "child": [], "normal": []}


def test_ticket_merge(ticket_pair):
    ticket_a, ticket_b = ticket_pair
    b_origin_article = ticket_b.articles[0]

    merged_ticket = ticket_b.merge_into(ticket_a.id)
    ticket_b.reload()

    assert merged_ticket == ticket_a
    assert merged_ticket.links() == {"child": [ticket_b], "parent": [], "normal": []}
    merged_articles = merged_ticket.articles
    assert len(merged_articles) == 3
    assert b_origin_article in merged_articles

    assert ticket_b.state.name == "merged"
    assert ticket_b.links() == {"child": [], "parent": [ticket_a], "normal": []}
    b_articles = ticket_b.articles
    assert len(b_articles) == 1
    assert b_articles[0].body == "merged"


def test_ticket_update(single_ticket):
    assert single_ticket.article_count == 1
    updated_ticket = single_ticket.update(body="new article")
    assert updated_ticket.article_count == 2


def test_ticket_create_article(single_ticket):
    assert single_ticket.article_count == 1
    new_article = single_ticket.create_article(body="new article")
    single_ticket.reload(expand=True)
    assert len(single_ticket.articles) == 2
    assert new_article.body == "new article"


def test_ticket_history(single_ticket):
    history = single_ticket.history()
    assert len(history) == 2

    assert history[0].items() > {"object": "Ticket", "type": "created"}.items()
    assert history[1].items() > {"object": "Ticket::Article", "type": "created"}.items()


def test_ticket_search(rclient, ticket_pair, record_log):
    """
    to ensure the search functionality zammad has to use the elasticsearch functionality
    the service must be running for this test to pass
    """
    if record_log[1]:
        time.sleep(5.0)
    tickets = list(rclient.tickets.search(f"title:__pytest__"))
    assert len(tickets) >= 2


def test_ticket_iter_with_offset(rclient, ticket_pair):
    tickets = list(rclient.tickets.iter(page=1000))
    assert len(tickets) == 0


def test_ticket_tags(single_ticket, assert_existing_tags):
    with assert_existing_tags("__pytest__", "__tag__"):
        assert single_ticket.tags() == []
        single_ticket.add_tags("__pytest__", "__tag__")
        assert single_ticket.tags() == ["__pytest__", "__tag__"]
        single_ticket.remove_tags("__tag__")
        assert single_ticket.tags() == ["__pytest__"]


def test_ticket_create_article_sender_and_type_attribute(single_ticket):
    assert single_ticket.create_article_sender == "Agent"
    assert single_ticket.create_article_type == "note"


def test_ticket_last_request_age_s(single_ticket):
    age_s = single_ticket.last_request_age_s()
    assert isinstance(age_s, float)
    assert age_s >= 0.0


def test_lazy_attribute_caching(caplog, rclient):
    import logging

    api_url = rclient.url
    ticket = rclient.tickets(1)

    with caplog.at_level(logging.INFO, logger="zammadoo"):
        _ = ticket["number"]
        with pytest.raises(KeyError):
            _ = ticket["doesnotexist"]

    # expect only one request without expand
    assert caplog.record_tuples == [
        ("zammadoo", logging.INFO, f"HTTP:GET {api_url}/tickets/1"),
    ]

    ticket = rclient.tickets(1)
    with caplog.at_level(logging.INFO, logger="zammadoo"):
        _ = ticket["owner"]
        with pytest.raises(KeyError):
            _ = ticket["stilldoesnotexist"]

    # expect one more request with expand
    assert caplog.record_tuples == [
        ("zammadoo", logging.INFO, f"HTTP:GET {api_url}/tickets/1"),
        ("zammadoo", logging.INFO, f"HTTP:GET {api_url}/tickets/1?expand=true"),
    ]
