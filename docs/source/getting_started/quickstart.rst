Quickstart
==========

This is what you'll need to run **clashcallerbot-reddit** :abbr:`ASAP (As Soon As Possible)`. **clashcallerbot-reddit**
is developed on various Linux distros, so :doc:`installation` is assumed to be on Linux.

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

Setup
-----

First, add the `bot's reddit metadata`_ to `praw-example.ini` and rename to `praw.ini`, then add the database's root and
desired bot user credentials to `database-example.ini` and rename to `database.ini`.

Next, change the following line in the :mod:`clashcallerbotreddit.database`

.. literalinclude:: ../../../clashcallerbotreddit/database.py
    :linenos:
    :lineno-start: 467
    :language: python
    :lines: 467-468

to ``database = ClashCallerDatabase(config_file=config, root_user=True)``. This may get updated to be default later.

Now, the MySQL-compatible database can be setup by running the :mod:`clashcallerbotreddit.database` directly from within
terminal::

    python3 -m clashcallerbotreddit.database

.. _bot's reddit metadata:
    https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html#defining-additional-sites

Starting
--------

Once the database is setup, the bot can be run by calling the :mod:`clashcallerbotreddit.search` and
the :mod:`clashcallerbotreddit.reply` directly from within terminal::

    python3 -m clashcallerbotreddit.search && python3 -m clashcallerbotreddit.reply

Alternatively, by running the provided bash script from within terminal::

    ./clashcallerbot.sh

.. note::

    * Remember to set executable mode with ``chmod +x ./clashcallerbot.sh``.
    * Script assumes files are in same directory and is run as crontab in :doc:`no_root_setup`.
    * How often to run as a crontab depends on how long you want the bot to be down/broken.
    * If you have access to root, check :doc:`installation` for info on setting up systemd instead.
    * Logfile can be removed if not necessary (remove variable and ``>> $logfile``).
    * ``python`` can be replaced with relevant python version.
    * The function in ``kill`` returns all script PIDs, so it must be restarted.
    * If you have access to ``pidof``, you can avoid killing all script instances.

Updating
--------

A bash script is also provided for updating and can be run directly from within terminal::

    ./redownload.sh

.. note::

    * Don't forget to set executable mode with ``chmod +x ./redownload.sh``.
    * Script assumes files are all in same directory and that it is run in a :doc:`no_root_setup`.
    * The ``-f`` and ``-q`` switch silence outputs to certain degrees.
