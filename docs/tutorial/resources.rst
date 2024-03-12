.. py:module:: zammadoo
   :noindex:

Objects can be lazy
===================

| Consider the following example:
| We enable logging and create a ticket object
  by its id. Then we print the ticket id, number and title.

.. code-block:: python

    import logging

    logging.basicConfig(level=logging.INFO)

    ticket = client.tickets(1)
    print(f"ticket id: {ticket.id}")
    print(f"ticket number: #{ticket.number}")
    print(f"ticket title: {ticket.title!r}")

    # ticket id: 1
    # INFO:zammadoo:HTTP:GET https://localhost/api/v1/tickets/1
    # ticket number: #67001
    # ticket title: 'Welcome to Zammad!'

What happened? Before printing the ticket number the client made a server request
to fetch the ticket data. This means if we instantiate an object it only contains
its id. The first time we get an attribute or perform a method which requires attributes
the data is queried from the server. This is called lazy object initialization and applies
to most resources.


Resource iteration
==================

If an endpoint supports listing you can simply use a *for loop* to iterate over all items.
In this example we refer to :attr:`client.Client.users` but the same applies to many other
endpoints (e.g. *tickets*, *organizations*, *groups*, *roles*, ...).

.. code-block:: python

    import logging

    logging.basicConfig(level=logging.INFO)

    for user in client.users:
        print(user.id, user.fullname)

    # INFO:zammadoo:HTTP:GET https://localhost/api/v1/users?page=1&per_page=10&expand=false
    # 1 -
    # 2 Nicole Braun
    # [user 3 to 10]
    # INFO:zammadoo:HTTP:GET https://localhost/api/v1/users?page=2&per_page=10&expand=false
    # [user 11 to 20]
    # INFO:zammadoo:HTTP:GET https://localhost/api/v1/users?page=3&per_page=10&expand=false
    # [user 21 to 30]

The Zammad API uses pagination and by default returns 10 items per request. If you want to use
different parameters for ``page`` or ``per_page`` you can use the :meth:`users.Users.iter` method.
Use `itertools.islice <https://docs.python.org/3/library/itertools.html#itertools.islice>`_
to limit the number of returned items, it's a Python iterable after all.

.. code-block:: python

    from itertools import islice

    # return only 6 users starting with page 10
    for user in islice(client.users.iter(page=10), 6):
        print(user.id, user.fullname)

    # INFO:zammadoo:HTTP:GET https://localhost/api/v1/users?page=10&per_page=10&expand=false
    # 91 Eric Idle
    # 92 Graham Chapman
    # 93 Michael Palin
    # 94 John Cleese
    # 95 Terry Jones
    # 96 Terry Gilliam


The same applies for :meth:`users.Users.search`.