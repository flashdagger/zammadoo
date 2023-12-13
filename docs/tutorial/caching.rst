Resource caching
================

When performing a ticket search, Zammad not only sends the ticket data but also
objects that are related like groups, users, roles and organizations. This reduces
the number of server requests.

By default, zammadoo caches almost every object data, so a request is only made if
the data is not in cache.

.. code-block:: python

    import logging

    logging.basicConfig(level=logging.INFO)

    for ticket in client.tickets.search("customer.fullname:Nicole Braun"):
        print(f"{ticket.title} by {ticket.customer.fullname} ({ticket.organization.name})")

    # INFO:zammadoo:HTTP:GET https://localhost/api/v1/tickets/search?query=customer.fullname%3ANicole+Braun&
    # Welcome to Zammad! by Nicole Braun (Zammad Foundation)
    # ...

In this example, we search for tickets, but also access data regarding users
(customer is a user) and organizations. As you can see in the logging output
no additional server requests are performed.

If we for example disable the caching, you can see that additional requests are made for
the customer's full name and the organization name.

.. code-block:: python

    client.users.cache.max_size = 0
    client.organizations.cache.max_size = 0

    for ticket in client.tickets.search("customer.fullname:Nicole Braun"):
        print(f"{ticket.title} by {ticket.customer.fullname} ({ticket.organization.name})")

    # INFO:zammadoo:HTTP:GET https://localhost/api/v1/tickets/search?query=customer.fullname%3ANicole+Braun&
    # INFO:zammadoo:HTTP:GET https://localhost/api/v1/users/2
    # INFO:zammadoo:HTTP:GET https://localhost/api/v1/organizations/1
    # Welcome to Zammad! by Nicole Braun (Zammad Foundation)
    # ...

For each resource, the cache can be controlled via setting the ``max_size`` property.
By default, max_size is set to ``-1`` which means the cache size is not limited.
``0`` disables caching completely and numbers greater than zero will limit the cache to
contain only the least recently used objects (LRU cache strategy).
To clear the cache completely, just call the ``clear()`` method.