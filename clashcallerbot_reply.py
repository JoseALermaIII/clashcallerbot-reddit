#! python3
# -*- coding: utf-8 -*-
"""Checks messages in database and sends PM if expiration time passed.

This module checks messages saved in a MySQL-compatible database and sends a reminder
via PM if the expiration time has passed. If so, the message is removed from the
database.
"""

import praw
import praw.exceptions

import logging.config
import datetime

import clashcallerbot_database as db

# Logger
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logging.raiseExceptions = True  # Production mode if False (no console sys.stderr output)
logger = logging.getLogger('reply')

# Generate reddit instance
reddit = praw.Reddit('clashcallerreply')  # Section name in praw.ini
subreddit = reddit.subreddit('ClashCallerBot')  # Limit scope for testing purposes


def main():
    while True:
        # Get list of messages older than current datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        messages = db.get_messages(now)

        if not messages:
            continue

        # TODO: Send reminder PM

        # TODO: Delete message from database


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
