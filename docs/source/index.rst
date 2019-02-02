.. clashcallerbot-reddit documentation master file, created by
   sphinx-quickstart on Fri Nov  2 03:04:11 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to clashcallerbot-reddit!
=================================

.. include:: ../../README.rst
   :start-after: reddit.**
   :end-before: Check us out

If not obvious enough, it's a fork of `SIlver--'s RemindMeBot <https://github.com/SIlver--/remindmebot-reddit>`_.
It's a sweet (as in awesome) little program.

I plan to make a few more tweaks to make it even more useful.

Check us out on `/r/ClashCallerBot <https://np.reddit.com/r/ClashCallerBot/>`_.

Usage Information
=================

Usage can be inferred from the regular expressions used to process each comment in :mod:`clashcallerbotreddit.search`:

.. literalinclude:: ../../clashcallerbotreddit/search.py
    :linenos:
    :lineno-start: 39
    :language: python
    :lines: 39-62

To sum:

* The ``clashcaller`` string must be present in either lower or CamelCase with an exclamation point ``!`` either
  before or after.
* The expiration time in minutes or hours may follow either abbreviated or with full spelling with an
  optional space between the number and word, but mandatory space after the word: ``4min``. Case is ignored. If not
  given, defaults to 1 hour. The expiration time is limited to within 24 hours.
* The message within quotes must follow with the singular or plural form of ``base`` and a required single or double
  digit number. Case is ignored. Maximum message length is 100 characters to save database space.

.. toctree::
   :maxdepth: 3
   :caption: Getting Started

   getting_started/quickstart
   getting_started/installation

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   modules

.. toctree::
   :maxdepth: 2
   :caption: About

   about/faqs
   about/references

.. toctree::
   :hidden:

   genindex
