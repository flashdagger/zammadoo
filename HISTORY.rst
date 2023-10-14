=======
History
=======

.. py:module:: zammadoo

future release
--------------
* **new feature**

    * added :meth:`tickets.Ticket.history` method
    * added ``weburl`` property for :class:`client.Client`, :class:`tickets.Ticket`,
      :class:`users.User` and :class:`organizations.Organization`

* **breaking changes**

    * :class:`client.Client` now uses ``http_auth=(username, password)`` as authentication parameter
    * for all ResourcesT like :class:`tickets.Tickets` ``.url`` is now a property
    * exchange ``tickets.Ticket.merge_with()`` with :meth:`tickets.Ticket.merge_into`
      mimicking the logic provided by the Web UI

* **fixes**

    * resource items are now cached when using iteration
    * fromisoformat conversion in Python 3.9 supporting Zulu offset format

0.1.0 (2023-10-08)
------------------
* initial release