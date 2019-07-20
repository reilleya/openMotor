Building openMotor from source
==============================

1. Install prerequisites
------------------------

``openMotor`` uses ``PyQt``, which in turn relies on Qt 5. To compile the UI
views, you will need to have Qt installed. The easiest way to do this is by
installing QtCreator, which will also give you access to the Qt Designer to
edit the view files. You can download `QtCreator here <https://www.qt.io/download-qt-installer>`_.

You also need to install openMotor's dependencies. The easiest way to do this
is with pip, inside a virtual environment:

\*nix
^^^^^

.. code-block:: console

    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt

Windows
^^^^^^^

.. code-block:: powershell

    PS> python -m venv .venv
    PS> .venv/Scripts/Activate.ps1
    (.venv) PS> pip install -r requirements.txt

If you get a security error, try using `Set-ExecutionPolicy <https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy>`_
to loosen your environment security settings.

2. Build Qt Views
-----------------

With QtCreator installed, compile the UI files:

.. code-block:: console

    $ python setup.py build_ui

3. Install openMotor in development mode
----------------------------------------

This will let you import the Python modules as if it were a normal package, but
is not necessary for the UI to work.

.. code-block:: console

    $ pip install -e .

Running openMotor
=================

Launching the UI is very easy:

.. code-block:: console

    $ python ./main.py

Building the Documentation
==========================

The documentation is written with Sphinx, and uses reStructuredText. The
necessary dependencies are included in the requirements file, so if you've
built from source you should be all set to build.

Run the following steps to build the docs:

.. code-block:: console

    $ cd ./docs
    $ sphinx-build -b html . _build

The build artifacts should now be present in ./docs/_build, and can be opened
in a normal web browser.
