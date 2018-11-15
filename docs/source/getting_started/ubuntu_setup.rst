:orphan:

Ubuntu 14.04 LTS Setup
======================

`Ubuntu Desktop <http://www.ubuntu.com/download>`_ is a good choice because most IDEs need a GUI, but other versions
are available (like Server). The following instructions are a combination of setting up the Ubuntu OS to run the bot
(build packages and setting up MySQL tables) as well as adding all the needed dependencies into python. Everything here
is run in a terminal.

First, enable compiling from source. There will be a lot of compiling from source in the future... ::

    sudo apt-get install build-essential python-dev libffi-dev libssl-dev

Next, set up pip::

    sudo apt-get install python-pip && sudo pip install pip

Then, `set up the needed environment
<http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/>`_. From within the virtual environment, run::

    sudo pip install praw

Now, setup MySQL/MariaDB. ::

    sudo apt-get install mysql-server # For MariaDB: sudo apt-get install mariadb-server mariadb
                                      # Set MySQL `root` pw when prompted (recommended)
    mysql_secure_installation         # say yes to everything after first prompt
    sudo apt-get install libmysqlclient-dev # For MariaDB: sudo apt-get install libmariadbclient-dev

From within the MySQL/MariaDB prompt, set up the database itself. ::

    mysql -uroot -p"password" # login as root
    CREATE DATABASE db_name;
    USE db_name;
    CREATE TABLE message_table (id INT UNSIGNED NOT NULL AUTO_INCREMENT, permalink VARCHAR(100), message VARCHAR(100),
    new_date DATETIME, userID VARCHAR(20), PRIMARY KEY(id));
    ALTER TABLE message_table AUTO_INCREMENT=1;
    CREATE TABLE comment_table (id MEDIUMINT NOT NULL, list VARCHAR(35), PRIMARY KEY(id));
    INSERT INTO comment_table VALUES (1, "'0'");
    GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES ON db_name.*
    TO 'botname'@localhost IDENTIFIED BY 'password';

Now that MySQL/MariaDB is set up, install more dependencies. ::

    source clashcallerbot-reddit/bin/activate    # set virtual environment, if needed
    sudo pip install mysql-connector

Start, redirect output, and background process. ::

    source clashcallerbot-reddit/bin/activate    # set virtual environment, if needed
    nohup python3 clashcallerbot_reply.py > /dev/null 2>&1 &
    nohup python3 clashcallerbot_search.py > /dev/null 2>&1 &

