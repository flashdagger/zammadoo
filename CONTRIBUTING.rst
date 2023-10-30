============
Contributing
============

How to develop on this project
==============================

Setting up your own virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The repository includes a Poetry_ ``pyproject.toml`` file to help you set up a
virtual environment and install the needed development dependencies. From the
repository checkout root directory execute::

    poetry install


Run the unit tests to ensure everything is working
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run ``pytest`` to run the tests. For details see the pytest_ project.


Create a new branch to work on your contribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run ``git checkout -b my_contribution``


Make your changes
^^^^^^^^^^^^^^^^^

Edit the files using your preferred editor. (we recommend VIM or VSCode)


Format the code
^^^^^^^^^^^^^^^

Run ``black zammadoo`` to format the code.


Run the linter
^^^^^^^^^^^^^^

Run ``pylint zammadoo`` to run the linter.


Test your changes
^^^^^^^^^^^^^^^^^

Run ``pytest`` to run the tests.
Ensure code coverage report in ``report/index.html`` shows `100%` coverage,
add tests to your PR.


Build the documentation locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sh

    # install the optional dependencies for building the documentation
    poetry install --with docs
    # build the HTML documents
    docs\make.bat html  # Windows
    make -C docs html   # Linux, MacOS


Open the ``docs/_build/html/index.html`` in your browser to ensure your new changes are documented.


Commit your changes and push to your fork
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run ``git push origin my_contribution``


Submit a pull request
^^^^^^^^^^^^^^^^^^^^^

On github interface, click on `Pull Request` button. Wait CI to run and one of the developers will review your PR.


.. _Poetry: https://python-poetry.org/
.. _pytest: https://www.pytest.org/
