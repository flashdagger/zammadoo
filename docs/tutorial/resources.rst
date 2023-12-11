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