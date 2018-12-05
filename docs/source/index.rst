.. clashcallerbot-reddit documentation master file, created by
   sphinx-quickstart on Fri Nov  2 03:04:11 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to clashcallerbot-reddit!
=================================

**ClashCallerBot** was made to help `/r/ClashOfClans <https://np.reddit.com/r/ClashOfClans>`_ clans coordinate attacks
during `Clan Wars <https://clashofclans.fandom.com/wiki/Clan_Wars>`_ (or `Clan War Leagues
<https://clashofclans.fandom.com/wiki/Clan_War_Leagues>`_) from within reddit.

For example, someone wants to attack base 1 and 7, but they haven't posted an update in over an hour
and those two bases still haven't been attacked. Is it okay to attack those bases? Did your fellow
clan member die? Who knows‽

Well, if s/he (or someone on their behalf) had called those bases for a set period of time, you would
know for certain.

Think of **ClashCallerBot** as an independent time keeper that runs entirely within reddit.

If not obvious enough, it's a fork of `SIlver--'s RemindMeBot <https://github.com/SIlver--/remindmebot-reddit>`_.
It's a sweet (as in awesome) little program.

I plan to make a few more tweaks to make it even more useful.

Check us out on `/r/ClashCallerBot <https://np.reddit.com/r/ClashCallerBot/>`_.

Usage Information
=================

Usage can be inferred from the regular expressions used to process each comment in the :doc:`search`:

.. literalinclude:: ../../clashcallerbotreddit/search.py
    :linenos:
    :lineno-start: 37
    :language: python
    :lines: 37-59

To sum:

* The ``clashcaller`` string must be present in either lower or camelcase with an exclamation point ``!`` either
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
