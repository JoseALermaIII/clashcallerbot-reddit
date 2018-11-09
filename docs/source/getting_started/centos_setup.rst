CentOS 7.0 Setup:
=================

How you want CentOS installed is your choice. I went with the `xxx-Minimal.iso <https://wiki.centos.org/Download>`_ so
that it would be as lean as possible (since I planned for it to be in the cloud) and would only be as large as necessary
to run the bot. Installation settings are also up to you (security, networking, user accounts, etc.). Since it is a
minimal install, there is no :abbr:`GUI (Graphical User Interface)` and everything is run from
:abbr:`tty1 (TeleTYpewriter number 1)`.

First, install :abbr:`EPEL (Extra Packages for Enterprise Linux)`. Pip isn't even available, so we start here::

    yum install epel-release

Enable compiling from source. The list of what won't be compiled from source is shorter. ::

    yum install gcc python-devel openssl-devel libffi-devel

Install and upgrade pip and wheel,::

    yum install python-pip python-wheel && pip install -U pip wheel

Then, `set up the needed environment
<http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/>`_. From within the virtual environment, run::

    pip install praw

Now, setup MySQL/MariaDB. ::

    yum install mariadb-server mariadb mariadb-devel
    systemctl start mariadb     # start mariadb
    systemctl enable mariadb     # start at boot
    systemctl status mariadb    # confirm installation
    mysql_secure_installation # Say yes to everything!
    mysql -uroot -p"password" # login to mysql

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

    source clashcallerbot-reddit/bin/activate    # set virtual environment, if needed
    pip install mysql-connector

Start, redirect output, and background process. ::

    source clashcallerbot-reddit/bin/activate    # set virtual environment, if needed
    nohup python clashcallerbot_reply.py > /dev/null 2>&1 &
    nohup python clashcallerbot_search.py > /dev/null 2>&1 &

.. tip::

    Alternatively, use `systemd service <https://stackoverflow.com/a/30189540)>`_.
