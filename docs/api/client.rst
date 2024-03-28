Client
======

.. py:module:: zammadoo.client

.. autoexception:: APIException
    :no-inherited-members:

.. autoclass:: Pagination
    :members:

.. autoclass:: Client
    :members:
    :exclude-members: get

    .. method:: get(*args, params=None)

       shortcut for :meth:`request` with parameter ``("GET", *args, params)``
