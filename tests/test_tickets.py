#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import Generator, Tuple

import pytest

from zammadoo.tickets import Ticket


def test_ticket_create_article_sender_attribute(client):
    ticket = client.tickets(123, info={"id": 123, "create_article_sender_id": 1})
    assert ticket.create_article_sender == "Agent"

    ticket = client.tickets(123, info={"id": 123, "create_article_sender_id": 2})
    assert ticket.create_article_sender == "Customer"

    ticket = client.tickets(123, info={"id": 123, "create_article_sender_id": 3})
    assert ticket.create_article_sender == "System"

    ticket = client.tickets(123, info={"id": 123, "create_article_sender_id": 4})
    assert ticket.create_article_sender == "Unknown"


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


@pytest.fixture(scope="function")
def ticket_pair(
    rclient, temporary_resources
) -> Generator[Tuple[Ticket, Ticket], None, None]:
    tickets = [
        {
            "title": "__pytest__",
            "customer_id": "guess:pytest@localhost.local",
            "group": "Users",
            "article": {"body": "..."},
        },
        {
            "title": "__pytest__",
            "customer_id": "guess:pytest@localhost.local",
            "group": "Users",
            "article": {"body": "..."},
        },
    ]

    with temporary_resources("tickets", *tickets) as infos:
        yield tuple(rclient.tickets(info["id"], info=info) for info in infos)


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
    assert len(merged_articles) == 2
    assert b_origin_article in merged_articles

    assert ticket_b.state.name == "merged"
    assert ticket_b.links() == {"child": [], "parent": [ticket_a], "normal": []}
    b_articles = ticket_b.articles
    assert len(b_articles) == 1
    assert b_articles[0].body == "merged"


def test_ticket_update(ticket_pair):
    ticket, _ = ticket_pair
    assert ticket.article_count == 1
    updated_ticket = ticket.update(body="new article")
    assert updated_ticket.article_count == 2


def test_ticket_create_article(ticket_pair):
    ticket, _ = ticket_pair
    assert ticket.article_count == 1
    new_article = ticket.create_article(body="new article")
    assert len(ticket.articles) == 2
    assert new_article.body == "new article"


def test_ticket_history(ticket_pair):
    ticket, _ = ticket_pair
    history = ticket.history()
    assert len(history) == 2

    assert history[0].items() > {"object": "Ticket", "type": "created"}.items()
    assert history[1].items() > {"object": "Ticket::Article", "type": "created"}.items()
