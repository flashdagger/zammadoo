========
zammadoo
========

.. image:: https://img.shields.io/pypi/l/zammadoo.svg
        :target: https://pypi.python.org/pypi/zammadoo/
        :alt: PyPI license

.. image:: https://readthedocs.org/projects/zammadoo/badge/?version=latest
        :target: https://zammadoo.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


an object-oriented REST API client for Zammad


Real life examples
------------------

.. code-block:: python

    from zammadoo import Client

    client = Client("https://myhost.com/api/v1/", username="<username>", password="<mysecret>")

    # I have a new ticket with id 17967 and I need to download the attachment file
    path = client.tickets(17967).articles[0].attachments[0].download()
    print(f"The downloaded file is {path}")

    # I need to close all tickets with the tag "deprecated" and remove the tag
    for ticket in client.tickets.search("tags:deprecated"):
        ticket.update(state="closed")
        ticket.remove_tags("deprecated")


design principles
-----------------

Zammadoo provides a fluent workflow. Since the provided resources are wrapped in its own type
your IDE can show you many of the available properties and methods.
