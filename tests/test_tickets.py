#!/usr/bin/env python
# -*- coding: UTF-8 -*-


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


def test_tickets_create(rclient, temporary_resources):
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

        article = ticket.articles[0]
        assert article.body == "article body"
        assert article.internal is False
