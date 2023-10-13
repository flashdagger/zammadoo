=======
History
=======

.. py:module:: zammadoo

future release
--------------
* **breaking change**: :class:`client.Client` now uses ``http_auth=(username, password)`` as authentication parameter
* **new feature**: :meth:`tickets.Ticket.history` method
* **fix**: resource items are now cached when using iteration
* **fix**: fromisoformat conversion in Python 3.9

0.1.0 (2023-10-08)
------------------
* initial release