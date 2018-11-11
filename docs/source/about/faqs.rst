FAQs
====

No one really asked them, but these are the anticipated :abbr:`FAQs (Frequently Asked Questions)`.

What is the point of ClashCallerBot?
------------------------------------

.. include:: ../index.rst
    :start-after: clashcallerbot-reddit!
    :end-before: Usage Information

Is it ready yet?
----------------

**Closed Beta** until I add a few more features. Let me know in `/r/ClashCallerBot
<https://np.reddit.com/r/ClashCallerBot/comments/4e9vo7/clashcallerbot_info/>`_ or via `PM
<https://www.reddit.com/message/compose/?to=ClashCallerBotDbuggr&subject=Closed%20Beta>`_ if you'd like your subreddit
to be added to the closed beta.

How do you call ClashCallerBot?
-------------------------------

``ClashCaller! TIME OPTION "REQUIRED MESSAGE" (with quotes)``

Time is optional (defaults to an hour); however, a message is required. Meaning if you do a simple ``ClashCaller!`` the
bot won't do anything, but you will contribute to spam. Ideally, the message will be something like "Base #3" or
something to indicate the base being called. Everything before ``ClashCaller!`` is not caught and everything after is.
So feel free to use it in long winded posts but make sure it's after to avoid problems.

The PM will give you the permalink to your original comment.

Do PMs work?
------------

No, they don't. Everyone needs to see what you called so they know not to attack it.

What options does it have?
--------------------------

All options are listed here:

.. include:: ../index.rst
    :start-after: Usage Information
    :end-before: toctree

**ClashCallerBot** will then make this comment and will message you at the given time::

    ClashCallerBot here!
    I will be messaging you on Nov. 10, 2018 at 10:30:29 AM (UTC) to remind you of **this call.**

    Thank you for entrusting us with your warring needs!

    [^(More info)](https://www.reddit.com/r/ClashCallerBot/comments/4e9vo7/clashcallerbot_info/)

The expiration time is limited to within 24 hours. Call messages can't be longer than 100 characters to save database
space. It is suggested that the bot be used with a multiple of an hour value, but minutes can also be used.

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
