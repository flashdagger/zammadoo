TimeAccountings
===============

.. py:module:: zammadoo.time_accountings

.. autoclass:: TimeAccountingType
    :members:
    :exclude-members: delete, update

    .. method:: delete()

        Since time_accounting types cannot be deletet via REST API,
        this method raises an exception.

        :raises: :exc:`NotImplementedError`

    .. method:: update(**kwargs)

        Update the type properties.

        :param kwargs: name(`str`), note(`note`) or active(`bool`)
        :return: a new type instance
        :rtype: :class:`TimeAccountingType`



.. autoclass:: TimeAccountingTypes
    :members:

.. autoclass:: TimeAccounting
    :members:
    :exclude-members: update

    .. method:: update(**kwargs):

        Update the time accounting properties. Required permission: ``admin.time_accounting``.

        examples::

            time_accounting = client.time_accountings(1)

            # time_unit can be ``float`` or ``str``
            new_instance = time_accounting.update(time_unit=60.0)

            # change accounting type: ``str`` or type_id: ``int``
            new_instance = time_accounting.update(type="research")

            # change accounting type to default
            new_instance = time_accounting.update(type_id=None)


        :return: a new instance of the updated time accounting
        :rtype: :class:`TimeAccounting`

.. autoclass:: TimeAccountings
    :members:
