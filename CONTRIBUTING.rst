============
Contributing
============

How to develop on this project
==============================

Get the code from the repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The development of *zammadoo* takes place on GitHub_.
The ``main`` branch should contain the most recent and working code.
For a checkout of the the files run ::

    git clone -b main https://github.com/flashdagger/zammadoo.git

If you have a GitHub account you can fork the project from https://github.com/flashdagger/zammadoo
and create your own development branch.


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

Add unit tests to your PR and run ``pytest`` to run the tests.
Ensure the code coverage report in ``report/index.html`` includes your changes.


Build the documentation locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sh

    # install the optional dependencies for building the documentation
    pip install -r docs/requirements.txt
    # build the HTML documents
    docs\make.bat html  # Windows
    make -C docs html   # Linux, MacOS


Open the ``docs/_build/html/index.html`` in your browser to ensure your new changes are documented.


Commit your changes and push to your fork
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run ``git push -u origin my_contribution``


Submit a pull request
^^^^^^^^^^^^^^^^^^^^^

On github interface, click on `Pull Request` button. Wait CI to run and one of the developers will review your PR.


.. _GitHub: https://github.com/
.. _Poetry: https://python-poetry.org/
.. _pytest: https://www.pytest.org/
