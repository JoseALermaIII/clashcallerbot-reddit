Installation
============

This thing has to run 24/7. As a proof of concept, I set it up in an Ubuntu VM for the open alpha and a CentOS VM
for the open beta. Production version was running on CloudLinux OS in a shared host at one point, but has since moved
to AWS. If you are using a different OS, your mileage may vary.

Deployment Options
------------------

Believe me, the list of where I have not deployed it is shorter. I mostly went with virtual machines for the
development, and had the production version on a shared host for a bit. It has been migrated to an Amazon EC2
instance in hopes of minimizing costs.

.. toctree::
    :maxdepth: 2

    ubuntu_setup
    centos_setup
    no_root_setup
    amazon_setup


Building Documentation
----------------------

.. note::

    Building the documentation is **not needed or recommended** unless contributing to the documentation. The latest
    version of the documentation is available at `josealermaiii@github.io/clashcallerbot-reddit
    <https://josealermaiii.github.io/clashcallerbot-reddit/>`_ or as a `PDF in the source code
    <https://github.com/JoseALermaIII/clashcallerbot-reddit/blob/master/clashcallerbot-reddit.pdf>`_. You have been warned.

Building the docs requires a few more pip packages:

* Sphinx
* sphinxcontrib-napoleon
* sphinx-rtd-theme

If that wasn't bad enough, a symbolic link to *praw.ini* must be made from within ``~/.config``.::

    cd ~/.config
    ln -s absolute_path_here/clashcallerbot-reddit/praw.ini praw.ini

This has to do with how `praw` finds the *praw.ini* file. This may get fixed later much like the *database.ini* fix in
`__init__.py`.

Now, we can build the docs in HTML format::

    cd absolute_path_here/clashcallerbot-reddit/docs
    make html

This will save the docs website in ``../../clashcallerbot-reddit-docs/``.

Building the PDF is even more involved. First, LaTeX must be installed on the OS. For example, in Ubuntu 18.04::

    sudo apt-get install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended

Installing these dependencies is not recommended, if not needed, because they require > 300 MB of disk space.

Now, we can build the docs in PDF format::

    cd absolute_path_here/clashcallerbot-reddit/docs
    make latexpdf

This will save the doc's PDF in ``../clashcallerbot-reddit.pdf``.

Disclaimer
----------

Though covered by the MIT License, I reiterate: executing code from the Internet in terminal can end up doing bad things.

    Read and understand all code you copy and paste before running it.
