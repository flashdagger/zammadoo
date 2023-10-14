========
zammadoo
========

.. image:: https://img.shields.io/pypi/v/zammadoo.svg
   :target: https://pypi.python.org/pypi/zammadoo/
   :alt: [Latest Version]

.. image:: https://img.shields.io/pypi/pyversions/zammadoo.svg
   :target: https://pypi.python.org/pypi/zammadoo/
   :alt: [Python versions]

.. image:: https://img.shields.io/pypi/l/zammadoo.svg
    :target: https://pypi.python.org/pypi/zammadoo/
    :alt: PyPI license

.. image:: https://github.com/flashdagger/zammadoo/actions/workflows/core-tests.yml/badge.svg?event=push
    :target: https://github.com/flashdagger/zammadoo/actions/workflows/core-tests.yml
    :alt: Core Tests


.. image:: https://readthedocs.org/projects/zammadoo/badge/?version=latest
    :target: https://zammadoo.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


an object-oriented REST API client for the `Zammad helpdesk sytem <https://zammad.org/>`_


Real life examples
------------------

.. code-block:: python

    from zammadoo import Client

    client = Client("https://myhost.com/api/v1/", http_auth=("<username>", "<mysecret>"))
    # or use an API token created via https://myhost.com/#profile/token_access
    client = Client("https://myhost.com/api/v1/", http_token="<token>")

    # I have a new ticket with id 17967 and need to download the attachment file
    path = client.tickets(17967).articles[0].attachments[0].download()
    print(f"The downloaded file is {path}")

    # I need to append a new ticket article with attached files
    client.ticket(17967).create_article("Server down again. See logfiles.", files=["kern.log", "syslog"])

    # I want to close all tickets with the tag "deprecated" and remove the tag
    for ticket in client.tickets.search("tags:deprecated"):
        ticket.update(state="closed")
        ticket.remove_tags("deprecated")


Design principles
-----------------

Zammadoo provides a fluent workflow. Since the resources are wrapped in its own type,
your IDE can show you many of the available properties and methods.
