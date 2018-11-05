Installation
============

This thing has to run 24/7. As a proof of concept, I set it up in an Ubuntu VM for the open alpha and a CentOS VM
for the open beta. Production version was running on CloudLinux OS at one point, but has since moved to Amazon Linux
AMI on AWS. If you are using a different OS, your mileage may vary.

Deployment Options
------------------

Believe me, the list of where I have not deployed it is shorter. I mostly went with virtual machines for the
development, and tried putting the production version on a shared host. It has been migrated to an Amazon EC2
instance in hopes of minimizing costs.

Ubuntu
^^^^^^

For the open alpha, I went with an OS that is convenient (need something? There's a package for that) as a proof
of concept and debugging environment.

:doc:`ubuntu_setup`

CentOS
^^^^^^

For the open beta, I went with an OS that is often available for production environments.

:doc:`centos_setup`

No Root
^^^^^^^

For my first attempt at a production version, I got a shared host running CloudLinux OS that does not provide
root access, but has both Python and MySQL pre-installed.

:doc:`no_root_setup`

Amazon EC2
^^^^^^^^^^

For what I hope is the final production version, I set up an Amazon EC2 instance running Amazon Linux AMI.
I particularly like that it has pip and python pre-installed.

:doc:`amazon_setup`

.. toctree::

   amazon_setup
   centos_setup
   no_root_setup
   ubuntu_setup

Building Documentation
----------------------

.. TODO: add section

Disclaimer
----------

Though covered by the MIT License, I reiterate: executing code from the Internet in terminal can end up doing bad things.

    Read and understand all code you copy and paste before running it.