=======
History
=======

.. py:module:: zammadoo

0.2.0 (tbd)
-----------
* **breaking changes**

    * :class:`client.Client` now uses ``http_auth=(username, password)`` as authentication parameter
    * for all ResourcesT like :class:`tickets.Tickets` ``.url`` is now a property
    * exchange ``tickets.Ticket.merge_with()`` with :meth:`tickets.Ticket.merge_into()`
      mimicking the logic provided by the Web UI
    * :meth:`tags.Tags.delete()` and :meth:`tags.Tags.delete()` now only accept the tag name
    * changed signature of :meth:`tickets.Tickets.create()` to assure an article body or the article itself is provided
    * remove :attr:`articles.Article.encoding` property

* **added features**

    * extend supported Python version to 3.8
    * added :meth:`tickets.Ticket.history` method
    * added ``weburl`` property for :class:`client.Client`, :class:`tickets.Ticket`,
      :class:`users.User` and :class:`organizations.Organization`
    * added property :attr:`tickets.Ticket.create_article_sender`

* **fixes**

    * resource items are now cached when using iteration
    * fromisoformat conversion in Python <3.10 supporting Zulu offset format
    * :class:`roles.Roles` and :class:`groups.Groups` wrongly supported `search`
    * use :attr:`requests.Response.apparent_encoding` when returning attachment content as text

0.1.0 (2023-10-08)
------------------
* initial release