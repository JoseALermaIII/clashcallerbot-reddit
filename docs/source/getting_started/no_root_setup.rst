No Root Setup:
==============

What system you install to is your choice, but this setup assumes a CloudLinux OS without root access and with both
Python and MySQL installed. Everything is run from terminal (ssh compatible).

.. note::

    If you have multiple Python versions, replace ``python`` and ``pip`` with your version, e.g.,
    ``python2.7 get-pip.py --user``, ``pip2.7 install --user -U pip wheel``.

Since root is not available, pip needs to be installed locally. ::

    wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py --user

To ``~/.bashrc``, add ``PATH=$PATH:~/.local/bin`` and ``PYTHONPATH=$PYTHONPATH:~/.local/lib/python/site-packages/``,
then run ``source ~./bashrc`` to apply changes.

Next, update pip and wheel, then install a few dependencies. ::

    pip install --user -U pip wheel
    pip install --user praw

From within the MySQL prompt, setup the database itself. ::

    CREATE DATABASE db_name;
    USE db_name;
    CREATE TABLE message_table (id INT UNSIGNED NOT NULL AUTO_INCREMENT, permalink VARCHAR(100), message VARCHAR(100),
    new_date DATETIME, userID VARCHAR(20), PRIMARY KEY(id));
    ALTER TABLE message_table AUTO_INCREMENT=1;
    CREATE TABLE comment_table (id MEDIUMINT NOT NULL, list VARCHAR(35), PRIMARY KEY(id));
    INSERT INTO comment_table VALUES (1, "'0'");
    GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES ON db_name.*
    TO 'botname'@localhost IDENTIFIED BY 'password';

Now that MySQL is setup, install more dependencies. ::

    pip install --user MySQL-python
    pip install  --user pytz
    pip install --user parsedatetime

Start, redirect output, and background process. ::

    nohup python clashcallerbot_reply.py > /dev/null 2>&1 &
    nohup python clashcallerbot_search.py > /dev/null 2>&1 &


.. tip::

    Alternatively, use `systemd service <https://stackoverflow.com/a/30189540)>`_.
