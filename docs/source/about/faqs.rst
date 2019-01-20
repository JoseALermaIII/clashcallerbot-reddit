FAQs
====

No one really asked them, but these are the anticipated :abbr:`FAQs (Frequently Asked Questions)`.

What is the point of ClashCallerBot?
------------------------------------

**ClashCallerBot** was made to help `/r/ClashOfClans <https://np.reddit.com/r/ClashOfClans>`_ clans coordinate attacks
during `Clan Wars <https://clashofclans.fandom.com/wiki/Clan_Wars>`_ (or `Clan War Leagues
<https://clashofclans.fandom.com/wiki/Clan_War_Leagues>`_) from within reddit.

For example, someone wants to attack base 1 and 7, but they haven't posted an update in over an hour
and those two bases still haven't been attacked. Is it okay to attack those bases? Did your fellow
clan member die? Who knows‽

Well, if they (or someone on their behalf) had called those bases for a set period of time, you would
know for certain.

Think of **ClashCallerBot** as an independent time keeper that runs entirely within reddit.

If not obvious enough, it's a fork of `SIlver--'s RemindMeBot <https://github.com/SIlver--/remindmebot-reddit>`_.
It's a sweet (as in awesome) little program.

I plan to make a few more tweaks to make it even more useful.

Is it ready yet?
----------------

What I thought I'd do was keep it in permanent **Open Beta**, like Google. Let me know in `/r/ClashCallerBot
<https://np.reddit.com/r/ClashCallerBot/>`_ or via `PM
<https://www.reddit.com/message/compose/?to=ClashCallerBotDbuggr&subject=Feedback>`_ when something breaks.

How do you call ClashCallerBot?
-------------------------------

``ClashCaller! OPTIONAL TIME "REQUIRED MESSAGE" (with quotes)``

Time is optional (defaults to an hour); however, a message is required. Meaning if you do a simple ``ClashCaller!`` the
bot won't do anything, but you will contribute to spam. Ideally, the message will be something like "Base #3" or
something to indicate the base being called. Everything before ``ClashCaller!`` is not caught and everything after is.
So feel free to use it in long winded posts but make sure it's after to avoid problems.

The PM will give you the permalink to your original comment.

Do PMs work?
------------

Kind of. Everyone needs to see what you called so they know not to attack it, so you cannot directly set a call via
PM.

However, **ClashCallerBot** can execute certain commands from the comment replies.

What options does it have?
--------------------------

Usage can be inferred from the regular expressions used to process each comment in :mod:`clashcallerbotreddit.search`:

.. literalinclude:: ../../../clashcallerbotreddit/search.py
    :linenos:
    :lineno-start: 37
    :language: python
    :lines: 37-59

To sum:

* The ``clashcaller`` string must be present in either lower or CamelCase with an exclamation point ``!`` either
  before or after.
* The expiration time in minutes or hours may follow either abbreviated or with full spelling with an
  optional space between the number and word, but mandatory space after the word: ``4min``. Case is ignored. If not
  given, defaults to 1 hour. The expiration time is limited to within 24 hours.
* The message within quotes must follow with the singular or plural form of ``base`` and a required single or double
  digit number. Case is ignored. Maximum message length is 100 characters to save database space.

**ClashCallerBot** will then make this comment and will message you at the given time::

    ClashCallerBot here!
    I will be messaging you on Nov. 10, 2018 at 10:30:29 AM (UTC) to remind you of **this call.**

    Thank you for entrusting us with your warring needs!

    [^(More info)](https://www.reddit.com/r/ClashCallerBot/comments/4e9vo7/clashcallerbot_info/)

Hey, why didn't it notice me?
-----------------------------

Whoops! You should delete your comment (cut down on spam) and try again. Sometimes the bot misses a comment because
there are too many comments happening at once on reddit, connection issues, my PC restarted, my Internet is down/too
slow, or I'm watching Netflix. Do not worry about the reminder though, as long you got the confirmation PM/comment,
the reminder PM will come. Worst case scenario is that it will come late if there are connection issues.

Also, make sure you are calling the bot correctly. Like so::

    ClashCaller! OPTIONAL TIME (default is an hour without it) "REQUIRED MESSAGE".

You must do it as ClashCaller! exactly because it is case sensitive.

Why was the message off by a few minutes?
-----------------------------------------

The bot currently goes to sleep every 2 minutes to save on resources. Meaning your message can be as late as 2 minutes
+ any connection issues it is having with reddit.

What happens if it gets banned?
-------------------------------

As long as it doesn't receive a global ban on reddit, it will get your message. For example, the bot is currently
banned on /r/AskReddit (all bots are). Although it won't send the message to your comment, it will PM you to confirm.

If you see others doing ClashCaller! and no response from the bot, no worries! PMs are private.

Can I delete my comment?
------------------------

Yes. The bot sends a PM to the username that called it. As long as you don't delete your account you'll get your
message. Note that if you delete your message  -- unless it's a top level comment -- it won't be able to return the
original parent comment.
