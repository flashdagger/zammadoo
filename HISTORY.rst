=======
History
=======

.. py:module:: zammadoo

0.2.0 (tbd)
-----------
* **added features**

    * extend support for Python 3.8
    * added :meth:`tickets.Ticket.history` method
    * added ``weburl`` property for :class:`client.Client`, :class:`tickets.Ticket`,
      :class:`users.User` and :class:`organizations.Organization`
    * added property :attr:`tickets.Ticket.create_article_sender`

* **breaking changes**

    * :class:`client.Client` now uses ``http_auth=(username, password)`` as authentication parameter
    * for all ResourcesT like :class:`tickets.Tickets` ``.url`` is now a property
    * exchange ``tickets.Ticket.merge_with()`` with :meth:`tickets.Ticket.merge_into`
      mimicking the logic provided by the Web UI
    * :meth:`tags.Tags.delete()` and :meth:`tags.Tags.delete()` now only accept the tag name
    * changed signature of :meth:`tickets.Ticket.create()` to assure an article body or the article itself is provided

* **fixes**

    * resource items are now cached when using iteration
    * fromisoformat conversion in Python <3.10 supporting Zulu offset format

0.1.0 (2023-10-08)
------------------
* initial release