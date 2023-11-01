#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pytest

from . import ticket_pair


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
        path_1.write_bytes(bytes(range(256)))

        attachment_infos = Attachment.info_from_files(path_0, path_1)

        assert attachment_infos[0]["filename"] == "attachment.log"
        assert attachment_infos[0]["data"] == "SGVsbG8gWmFtbWFkIQ=="
        assert attachment_infos[0]["mime-type"] == "text/plain"

        assert attachment_infos[1]["mime-type"] == "application/octet-stream"


def test_create_article_via_ticket(ticket_pair):
    from pathlib import Path
    from tempfile import TemporaryDirectory

    ticket, _ = ticket_pair
    assert ticket.article_count == 1
    assert len(ticket.articles) == 1

    filename_text, content_text = "attachment.txt", "Mogę jeść szkło, i mi nie szkodzi."
    filename_binary, content_binary = "attachment.bin", bytes(range(256))

    with TemporaryDirectory() as tmpdir:
        textfile = Path(tmpdir, filename_text)
        textfile.write_text(content_text)
        binfile = Path(tmpdir, filename_binary)
        binfile.write_bytes(content_binary)

        ticket.create_article("pytest article #1", files=textfile)
        created_article = ticket.create_article(
            "pytest article #0", files=[textfile, binfile]
        )

    ticket.reload(expand=True)
    article = ticket.articles[-1]
    assert article == created_article
    assert article.body == "pytest article #0"

    text_attachment, binary_attachment = tuple(article.attachments)

    assert binary_attachment.filename == filename_binary
    assert binary_attachment.size == 256
    assert binary_attachment.read_bytes() == content_binary
    with pytest.raises(AssertionError, match="content is binary only"):
        binary_attachment.iter_text()

    assert text_attachment.filename == filename_text
    assert text_attachment.read_text() == content_text
    assert tuple(text_attachment.iter_text(chunk_size=16)) == (
        "Mogę jeść szk",
        "ło, i mi nie sz",
        "kodzi.",
    )

    with TemporaryDirectory() as tmpdir:
        downloaded_file = binary_attachment.download(tmpdir)
        assert downloaded_file == Path(tmpdir, filename_binary)
        assert downloaded_file.read_bytes() == content_binary

        downloaded_file = text_attachment.download(tmpdir)
        assert downloaded_file == Path(tmpdir, filename_text)
        assert downloaded_file.read_text() == content_text
