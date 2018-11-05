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
import time

from clashcallerbot_database import ClashCallerDatabase
from logging_conf import LOGGING
from config import config

# Logger
logging.config.dictConfig(LOGGING)
logging.raiseExceptions = True  # Production mode if False (no console sys.stderr output)
logger = logging.getLogger('reply')

# Generate reddit instance
reddit = praw.Reddit('clashcallerreply')  # Section name in praw.ini
subreddit = reddit.subreddit('ClashCallerBot')  # Limit scope for testing purposes

# Make database instance
db = ClashCallerDatabase(config, False)


def main():
    logger.info('Start reply.py...')
    while True:
        time.sleep(30)
        db.open_connections()
        # Get list of messages older than current datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        messages = db.get_messages(now)

        if not messages:
            logger.debug(f'No messages before: {now}.')
            db.close_connections()
            continue

        # Send reminder PM
        for message in messages:
            tid, link, msg, _exp, usr = message
            logger.debug(f'Found message: {message}')
            if send_reminder(link, msg, usr):
                logger.info(f'Reminder sent to {usr}.')

            # Delete message from database
            if db.delete_message(tid):
                logger.info(f'Message deleted.')
        db.close_connections()


def send_reminder(link: str, msg: str, usr: str)-> bool:
    """Sends reminder PM to username.

    Function sends given permalink and message to given username.

    Args:
         link:  Permalink to comment.
         msg:   Message in comment that was saved.
         usr:   User to send reminder to.

    Returns:
        True if successful, False otherwise.
    """
    subject = 'ClashCallerBot Private Message Here!'
    permalink = 'https://np.reddit.com' + link  # Permalinks are missing prefix
    parent = get_parent(link)
    message = f"""**The message:** {msg}  
              **The original comment:** {permalink}  
              **The parent comment or submission:** {parent}  

              Thank you for entrusting us with your warring needs,  
              - ClashCallerBot

              [^(More info)](https://www.reddit.com/r/ClashCallerBot/comments/4e9vo7/clashcallerbot_info/)
              """
    try:
        reddit.redditor(usr).message(subject, message.replace('              ', ''))

    except praw.exceptions.PRAWException as err:
        logger.exception(f'send_reminder: {err}')
        return False
    return True


def get_parent(link: str) -> str:
    """Fetch parent comment or submission.

    Function gets parent comment of given permalink or submission if top level comment.

    Args:
         link:  Permalink to get parent of.

    Returns:
        Parent comment link or default string.
    """
    permalink = 'https://www.reddit.com' + link  # Permalink is missing prefix
    parent = 'Parent comment not found.'  # Default string
    try:
        comment = reddit.comment(url=permalink)  # Fetch comment by URL
        parent = 'https://np.reddit.com' + comment.submission.permalink
    except praw.exceptions as err:
        logger.exception(f'get_parent: {err}')
        return parent
    return parent


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
