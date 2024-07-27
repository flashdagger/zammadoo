=======
History
=======

.. py:module:: zammadoo

0.4.0 (unreleased)
------------------
* **breaking changes**

    * :class:`Resource` class: replace :meth:`last_request_at()` with :meth:`last_request_age_s()`
      (e.g see :meth:`tickets.Ticket.last_request_age_s()`)

* **added features**

    * none yet

* **fixes**

    * none yet

0.3.0 (2024-07-25)
------------------
* **breaking changes**

    * none

* **added features**

    * added ``raise_if_exists`` parameter to :meth:`articles.Attachment.download` method
    * added support for the ``/time_accountings`` endpoint (for details see :doc:`api/time_accountings`)
    * added :meth:`tickets.Ticket.time_accountings` and :meth:`tickets.Ticket.create_time_accounting`
    * added :meth:`articles.Article.create_or_update_time_accounting`
    * added support for the ``/online_notifications`` endpoint (for details see :doc:`api/notifications`)
    * force requests with ``'expand=true'`` if ``'*'`` in :attr:`EXPANDED_ATTRIBUTES`

* **fixes**

    * fix edge case when unexpanded attributes were cached but a new instance accessed an expanded attribute
    * update ``EXPANDED_ATTRIBUTES`` on classes

0.2.0 (2024-03-10)
------------------
* **breaking changes**

    * :class:`client.Client` now uses ``http_auth=(username, password)`` as authentication parameter
    * for all ResourcesT like :class:`tickets.Tickets` ``.url`` is now a property
    * exchange ``tickets.Ticket.merge_with()`` with :meth:`tickets.Ticket.merge_into()`
      mimicking the logic provided by the Web UI
    * :meth:`tags.Tags.delete()` and :meth:`tags.Tags.rename()` now only accept the tag name
    * changed signature of :meth:`tickets.Tickets.create()` to assure an article body or the article itself is provided
    * remove :attr:`articles.Article.encoding` property

* **added features**

    * extend supported Python version including Python 3.8
    * added :meth:`tickets.Ticket.history` method
    * added ``weburl`` property for :class:`client.Client`, :class:`tickets.Ticket`,
      :class:`users.User` and :class:`organizations.Organization`
    * added property :attr:`tickets.Ticket.create_article_sender`
    * added property :attr:`groups.Group.parent_group`
    * save timestamp when cache is updated, added method :meth:`tickets.Ticket.last_request_at`
    * ``dir(Resource)`` now also returns the dynamic attributes

* **fixes**

    * resource items are now cached when using iteration
    * fromisoformat conversion in Python <3.10 supporting Zulu offset format
    * :class:`roles.Roles` and :class:`groups.Groups` wrongly supported `search`
    * use :attr:`requests.Response.apparent_encoding` when returning attachment content as text

0.1.0 (2023-10-08)
------------------
* initial release