Amazon Linux 2 Setup
====================

For what is intended to be the final production version, an Amazon EC2 instance is running Amazon Linux 2.
Amazon Linux 2 includes such conveniences as pip and python pre-installed.

Setup Amazon Linux 2
--------------------

`Amazon Linux 2`_ is Amazon's latest version of Amazon Linux. According to :abbr:`OS (Operating System)` metadata,
Amazon Linux 2 *may be* a fork of :abbr:`RHEL7 (Red Hat Enterprise Linux version 7)` or the equivalent Fedora version,
but built to run on the :abbr:`EC2 (Amazon Elastic Compute Cloud)` of :abbr:`AWS (Amazon Web Services)`. It is a good
choice for having an operating system that is fully up to date and supported by the "host." I particularly like that
it is already setup with most of what is needed. If preferred, use Ubuntu, OpenSUSE, Red Hat, et al., but your mileage
will vary using this guide.

.. tip::

    Check out the :doc:`CentOS Setup Guide <centos_setup>` or the :doc:`Ubuntu Setup Guide <ubuntu_setup>` if using
    those distros.

`Get an AWS account set up/prep for using EC2`_, then `set up the EC2 instance`_ itself. It is a bit of an
orchestration, but worth it.

.. note::

    * Opted for a ``t3.micro`` instance since that's what's 'in' right now.
      Also used Security Groups to limit access to My IP and used a key pair.
    * It is a good idea to `enable billing alerts`_.
    * The root volume is deleted on termination of the instance, so I enabled termination protection. Alternatively,
      the root volume can be `changed to persist`_.

`Configure`_ an :abbr:`EBS (Elastic Block Store)` to store the database. Went with 20 GB since that should be more
than enough. Also went with magnetic storage because it costs less than SSD storage and the I/O speed is not needed.

.. tip::

    * Adding tags helps keep instances organized, like
      ``Name: ClashCallerBot, Category: EC2 t3.micro, Stack: Production``, etc
    * When connecting from Windows operating systems, I prefer `PuTTY`_/`KiTTY`_, but there is a `doc detailing setup`_.

Next, `secure the EC2 instance`_. It is an old guide, so the only thing that needs to be done is adding a new user
(with limited access, by default) to run the bot. At this point, a `root volume snapshot can be made`_ to save
progress, if persistence was not enabled previously.

.. tip::

    * `Install and enable yum-cron`_ to keep the EC2 instance updated automatically.

.. _Amazon Linux 2: https://aws.amazon.com/amazon-linux-2/
.. _Get an AWS account set up/prep for using EC2:
    http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html
.. _set up the EC2 instance: https://aws.amazon.com/ec2/getting-started/
.. _enable billing alerts:
    http://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html#turning_on_billing_metrics
.. _Configure: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-creating-volume.html
.. _changed to persist:
    http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/RootDeviceStorage.html#Using_RootDeviceStorage
.. _PuTTY: http://www.chiark.greenend.org.uk/~sgtatham/putty/
.. _KiTTY: http://www.9bis.net/kitty/
.. _doc detailing setup: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html
.. _secure the EC2 instance: https://aws.amazon.com/articles/tips-for-securing-your-ec2-instance/
.. _root volume snapshot can be made: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html
.. _Install and enable yum-cron:
    https://community.centminmod.com/threads/automatic-nightly-yum-updates-with-yum-cron.1507/?PageSpeed=noscript

Setup pip and python
--------------------

Install some dependencies as the **default user**, not the new one. ::

    sudo yum install gcc python36-devel.x86_64 openssl-devel libffi-devel
    sudo pip install --upgrade pip

As the **new user**, `set up the needed environment`_ and select it from within the package directory::

    python3 -m venv clashcallerbot-reddit/env
    source clashcallerbot-reddit/env/bin/activate  # selects venv

From within the virtual environment, run::

    pip install -U wheel
    pip install --upgrade pip
    pip install praw
    pip install mysql-connector

.. _set up the needed environment: https://docs.python.org/3.6/library/venv.html#module-venv

Setup MySQL
-----------

`Set up a MySQL database within an EBS volume`_ as the **default user**. The guide is for Ubuntu, but setup for Amazon
Linux 2 is very similar (replace ``apt-get`` with ``yum`` and use ``sudo service mysqld [start|stop]`` to start or
stop MySQL). Once the EBS volume is created and attached, the **default user** needs to run the following from within
the EC2 instance to create an XFS filesystem at ``/vol``::

    # Create XFS filesystem
    sudo yum install xfsprogs mysql-server mysql-devel
    grep -q xfs /proc/filesystems || sudo modprobe xfs
    sudo mkfs.xfs /dev/sdb # change to wherever volume is mounted

    # Mount XFS filesystem
    echo "/dev/sdb /vol xfs noatime 0 0" | sudo tee -a /etc/fstab
    sudo mkdir -m 000 /vol
    sudo mount /vol

Now that MySQL is installed, it must be configured. ::

    sudo service mysqld start
    sudo service mysqld status    # Confirm it is running
    sudo mysql_secure_installation    # Say 'y' to everything!
    sudo mysql -uroot -p"password"

From within the MySQL prompt, ``mysql>``, the database can be set up. ::

    CREATE DATABASE db_name;
    USE db_name;
    CREATE TABLE message_table (id INT UNSIGNED NOT NULL AUTO_INCREMENT, permalink VARCHAR(100), message VARCHAR(100),
    new_date DATETIME, userID VARCHAR(20), PRIMARY KEY(id));
    ALTER TABLE message_table AUTO_INCREMENT=1;
    CREATE TABLE comment_table (id MEDIUMINT NOT NULL, list VARCHAR(35), PRIMARY KEY(id));
    INSERT INTO comment_table VALUES (1, "'0'");
    GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, ALTER ON db_name.* TO 'botname'@localhost IDENTIFIED BY
    'password';
    QUIT

Make sure that MySQL is stopped with ``sudo service mysqld stop && sudo service mysqld status``, then move MySQL into
the EBS volume. ::

    sudo mkdir /vol/etc /vol/lib /vol/log
    sudo mv /etc/my.cnf /vol/etc/
    sudo mv /var/lib/mysql /vol/lib/
    sudo mv /var/log/mysqld.log /vol/log

    sudo ln -s /vol/etc/my.cnf /etc/my.cnf
    sudo ln -s /vol/log/mysqld.log /var/log/mysqld.log

    sudo mkdir /var/lib/mysql
    echo "/vol/lib/mysql /var/lib/mysql none bind" | sudo tee -a /etc/fstab
    sudo mount /var/lib/mysql

    sudo service mysqld start && sudo service mysqld status
    sudo chkconfig --level 3 mysqld on  # set to start at boot

.. _Set up a MySQL database within an EBS volume: https://aws.amazon.com/articles/1663

Setup ClashCallerBot
--------------------

Now that python, pip, and MySQL have been set up, the **new user** can download and setup the bot::

    source clashcallerbot-reddit/env/bin/activate    # set virtual environment, if needed
    wget https://github.com/JoseALermaIII/clashcallerbot-reddit/raw/master/update.sh
    chmod +x ./update.sh
    ./update.sh

Next, add the `bot's reddit metadata`_ to `praw-example.ini` and rename to `praw.ini`, then add the database's root and
desired bot user credentials to `database-example.ini` and rename to `database.ini`.

Once all relevant files have been downloaded and configured, the bot can be started::

    chmod +x ./clashcallerbot.sh
    ./clashcallerbot.sh

.. tip::

    * The bot has to login to reddit at least once to refresh the oauth token. Amazon Linux 2 does not have a web
      browser installed by default, so run ``sudo yum install lynx`` as the **default user** before running the script.

.. _bot's reddit metadata:
    https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html#defining-additional-sites
