#!/usr/bin/env python
# -*- coding: UTF-8 -*-


def test_article_created_by_attribute(client):
    article = client.ticket_articles(1, info={"id": 1, "created_by_id": 2})
    assert article.created_by == client.users(2)


def test_article_origin_by_attribute(client):
    article = client.ticket_articles(1, info={"id": 1, "origin_by_id": 2})
    assert article.origin_by == client.users(2)


def test_article_updated_by_attribute(client):
    article = client.ticket_articles(1, info={"id": 1, "updated_by_id": 2})
    assert article.updated_by == client.users(2)


def test_article_ticket_attribute(client):
    article = client.ticket_articles(1, info={"id": 1, "ticket_id": 12345})
    assert article.ticket == client.tickets(12345)


def test_article_attachments_attribute(client):
    attachments = [
        {
            "id": 89,
            "store_file_id": 12,
            "filename": "zammad_logo_white.png",
            "size": "3253",
            "preferences": {
                "Mime-Type": "image/png",
                "resizable": True,
                "content_preview": True,
            },
        }
    ]
    article = client.ticket_articles(
        67, info={"id": 67, "ticket_id": 12345, "attachments": attachments}
    )
    attachment = article.attachments[0]

    assert attachment.url == f"{client.url}/ticket_attachment/12345/67/89"
    assert (
        repr(attachment) == f"<Attachment '{client.url}/ticket_attachment/12345/67/89'>"
    )
    assert attachment.filename == "zammad_logo_white.png"
    assert attachment.encoding is None
    assert attachment.size == 3253
    assert attachment.view()["size"] == "3253"


def test_attachment_create_info():
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from zammadoo.articles import Attachment

    with TemporaryDirectory() as tmpdir:
        path_0 = Path(tmpdir, "attachment.log")
        path_0.write_text("Hello Zammad!")

        path_1 = Path(tmpdir, "attachment.uknown")
        path_1.write_bytes(b"\xff")

        attachment_infos = Attachment.info_from_files(path_0, path_1)

        assert attachment_infos[0]["filename"] == "attachment.log"
        assert attachment_infos[0]["data"] == "SGVsbG8gWmFtbWFkIQ=="
        assert attachment_infos[0]["mime-type"] == "text/plain"

        assert attachment_infos[1]["mime-type"] == "application/octet-stream"
