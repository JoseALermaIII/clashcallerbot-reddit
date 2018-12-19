Quickstart
==========

This is what you'll need to run **clashcallerbot-reddit** :abbr:`ASAP (As Soon As Possible)`. **clashcallerbot-reddit**
is developed on various Linux distros, so :doc:`installation` is assumed to be on Linux.

We'll cover running installing into Python and running the scripts directly.

Prerequisites
-------------

:Python: clashcallerbot-reddit is a massive `python` script, so at least `Python 3.6`_ is needed.

:Pip: Configuring `python` is easiest using `pip`_. Once pip is installed, the requirements can be installed by
      running ``pip install -r requirements.txt`` from within the source code directory.

:MySQL: clashcallerbot-reddit uses a MySQL-compatible database to store calls and to keep track of comments that
        were replied to. Either `MySQL`_ or `MariaDB`_ can be used.

.. _Python 3.6: https://www.python.org/downloads/
.. _pip: https://pip.pypa.io/en/stable/installing/
.. _MySQL: https://dev.mysql.com/doc/en/installing.html
.. _MariaDB: https://mariadb.com/kb/en/library/where-to-download-mariadb/

With these prerequisites met, **clashcallerbot-reddit** can be setup and run.

Python Installation
-------------------

You're a brave one. This method is arguably faster; however, including a setup.py file is merely convention. This method
will install the internal modules into the Python environment so that they can be called directly as programs.

Setup
^^^^^

First, add the `bot's reddit metadata`_ to `praw-example.ini` and rename to `praw.ini`, then add the database's root and
desired bot user credentials to `database-example.ini` and rename to `database.ini`. Then, create a ``logs`` directory
by entering ``mkdir ./logs`` in a terminal window.

Next, change the following line in :mod:`clashcallerbotreddit.database`

.. literalinclude:: ../../../clashcallerbotreddit/database.py
    :linenos:
    :lineno-start: 402
    :language: python
    :lines: 402-403

to ``database = ClashCallerDatabase(config_file=config, root_user=True)``. This may get updated to be default later.

Starting
^^^^^^^^

Once the database script is setup, **clashcallerbot-reddit** can be installed by entering::

    python3 setup.py install

from within the source code directory. Now that **clashcallerbot-reddit** is installed, scripts can be run from
terminal directly. First, we configure the the MySQL-compatible database by running :mod:`clashcallerbotreddit.database`
in terminal::

    database

Now, the bot can be started by calling :mod:`clashcallerbotreddit.search` and :mod:`clashcallerbotreddit.reply`::

    nohup reply > /dev/null 2>&1 &
    nohup search > /dev/null 2>&1 &

.. warning::
    This will **not** check for already running instances! Any running instances would have to be terminated manually.
    Instances will appear with process names ``search`` and ``reply``.

Running Scripts Directly
------------------------

Not gonna lie, I'm a run scripts directly kind of guy. :abbr:`IMO (In My Opinion)`, it's less hassle and more secure to
do so, but :abbr:`YMMV (Your Mileage May Vary)`.

Setup
^^^^^

.. include:: ./quickstart.rst
    :start-after: ^^^^^
    :end-before: Starting

Now, the MySQL-compatible database can be setup by running :mod:`clashcallerbotreddit.database` directly from within
terminal::

    python3 -m clashcallerbotreddit.database

.. _bot's reddit metadata:
    https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html#defining-additional-sites

Starting
^^^^^^^^

Once the database is setup, the bot can be run by calling :mod:`clashcallerbotreddit.search` and
:mod:`clashcallerbotreddit.reply` directly from within terminal::

    python3 -m clashcallerbotreddit.search && python3 -m clashcallerbotreddit.reply

Alternatively, by running the provided bash script from within terminal::

    ./clashcallerbot.sh

.. note::

    * Remember to set executable mode with ``chmod +x ./clashcallerbot.sh``.
    * Script assumes files are in the `clashcallerbotreddit` directory and is run as crontab in :doc:`no_root_setup`.
    * How often to run as a crontab depends on how long you want the bot to be down/broken.
    * If you have access to root, check :doc:`installation` for info on setting up systemd instead.
    * Logfile can be removed if not necessary (remove variable and ``>> $logfile``).
    * ``python`` can be replaced with relevant python version.
    * The function in ``kill`` returns all script PIDs, so it must be restarted.
    * If you have access to ``pidof``, you can avoid killing all script instances.

Restarting
^^^^^^^^^^

A bash script is provided to restart both scripts and can be run from within terminal::

    ./restart.sh

.. note::

    * Remember to set executable mode with `chmod +x ./restart.sh`
    * Script assumes files are in the `clashcallerbotreddit` directory.
    * If you have access to root, check :doc:`installation` for info on setting up systemd instead.
    * Logfile can be removed if not necessary (remove variable and `>> $logfile`).
    * `python` can be replaced with relevant python version.
    * The function in `kill` returns all script PIDs, so it must be restarted.
    * If you have access to `pidof`, you can avoid killing all script instances.

Updating
^^^^^^^^

A bash script is also provided for updating both scripts and can be run directly from within terminal::

    ./update.sh

.. note::

    * Don't forget to set executable mode with ``chmod +x ./update.sh``.
    * The ``-f`` and ``-q`` switch silence outputs to certain degrees.
