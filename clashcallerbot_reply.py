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
        # TODO: Get list of messages ordered by expiration date (in MySQL)

        # TODO: Compare each message expiration datetime to current datetime (in MySQL?)

        # TODO: If current datetime is after expiration datetime, send PM

        # TODO: Delete message from database
        pass


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
