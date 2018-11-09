Quickstart
==========

This is what you'll need to run **clashcallerbot-reddit** :abbr:`ASAP (As Soon As Possible)`. **clashcallerbot-reddit**
is developed on various Linux distros, so :doc:`installation` is assumed to be on Linux.

Prerequisites
-------------

:Python: **clashcallerbot-reddit** is a massive `python` script, so at least `Python 3.6`_ is needed.

:Pip: Configuring `python` is easiest using `pip`_. Once pip is installed, the requirements can be installed by
      running ``pip install -r requirements.txt`` from within the source code directory.

:MySQL: **clashcallerbot-reddit** uses a MySQL-compatible database to store calls and to keep track of comments that
        were replied to. Either `MySQL`_ or `MariaDB`_ can be used.

.. _Python 3.6: https://www.python.org/downloads/
.. _pip: https://pip.pypa.io/en/stable/installing/
.. _MySQL: https://dev.mysql.com/doc/en/installing.html
.. _MariaDB: https://mariadb.com/kb/en/library/where-to-download-mariadb/

With these prerequisites met, **clashcallerbot-reddit** can be setup and run.

Setup
-----

First, add the database's root and desired bot user credentials to `database-example.ini`.

Next, change the following line in :doc:`../clashcallerbot_database`

.. literalinclude:: ../../../clashcallerbot_database.py
    :linenos:
    :lineno-start: 462
    :language: python
    :lines: 462-463

to ``database = ClashCallerDatabase(config_file=config, root_user=True)``. This may get updated to be default later.

Now, the MySQL-compatible database can be setup by running clashcallerbot_database.py directly from within terminal::

    python3 ./clashcallerbot_database.py

Starting
--------

Once the database is setup, the bot can be run by calling :doc:`../clashcallerbot_search` and
:doc:`../clashcallerbot_reply` directly from within terminal::

    python3 ./clashcallerbot_search.py && python3 ./clashcallerbot_reply.py

Alternatively, by running the provided bash script from within terminal::

    ./clashcallerbot.sh

.. note::

    * Remember to set executable mode with ``chmod +x ./clashcallerbot.sh``.
    * Script assumes files are in same directory and is run as crontab in :doc:`no_root_setup`.
    * How often to run as a crontab depends on how long you want the bot to be down/broken.
    * If you have access to root, check :doc:`installation` for info on setting up systemd instead.
    * Logfile can be removed if not necessary (remove variable and ``>> $logfile``).
    * ``python2.7`` can be replaced with relevant python version.
    * The function in ``kill`` returns all script PIDs, so it must be restarted.
    * If you have access to ``pidof``, you can avoid killing all script instances.

Updating
--------

A bash script is also provided for updating and can be run directly from within terminal::

    ./redownload.sh

.. note::

    * Don't forget to set executable mode with ``chmod +x ./redownload.sh``.
    * Script assumes files are all in same directory and that it is run in a :doc:`no_root_setup`.
    * The ``-f`` switch and ``> /dev/null 2>&1`` silence outputs to certain degrees.
