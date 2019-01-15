#! python3
# -*- coding: utf-8 -*-
"""Performs cleanup operations.

This module implements functions designed to clean up various data sets:

* Sends and deletes stored messages in the MySQL-compatible database.
* Checks bot's comments and removes comments below a certain threshold.
* TODO: Checks bot's messages for keywords and deletes them after:

    * Adding message author to call reminder.
    * PMing list of message author's calls.
    * Deleting message author from call.

"""

import praw
import praw.exceptions

import logging.config
import datetime
import time

from clashcallerbotreddit.database import ClashCallerDatabase
from clashcallerbotreddit.search import is_recent
from clashcallerbotreddit import LOGGING, config

# Logger
logging.config.dictConfig(LOGGING)
logging.raiseExceptions = True  # Production mode if False (no console sys.stderr output)
logger = logging.getLogger('reply')

# Generate reddit instance
reddit = praw.Reddit('clashcallerreply')  # Section name in praw.ini
subreddit = reddit.subreddit('ClashCallerBot')  # Limit scope for testing purposes

# Make database instance
db = ClashCallerDatabase(config, root_user=False)

# Time constants
start_time = datetime.datetime.now(datetime.timezone.utc)
archive_time = start_time - datetime.timedelta(weeks=12)  # 6 months archival time


def main():
    logger.info('Start reply.py...')
    while True:
        # Check saved messages
        check_database()

        # Check for comments below threshold
        check_comments('ClashCallerBot')

        time.sleep(120)  # 2 minutes


def check_comments(usr: str, limit: int = -4)-> None:
    """Checks comments and deletes if below threshold.

    Checks given user's last 100 comments and deletes each one below the given threshold.

    Args:
        usr: User to check comments of.
        limit: Threshold below which comment will be deleted. Defaults to ``-4``.

    Returns:
         None. Comments below threshold are deleted.

    Note:
        Skips archived comments (> 6 months from start time).

    """
    try:
        comments = reddit.redditor(usr).comments.new()
        for comment in comments:
            if not is_recent(comment.created_utc, archive_time):
                logger.info(f'Skipping comments after {archive_time}.')
                return None

            if comment.score < limit:
                logger.info(f'Deleting comment below threshold of {limit}: {comment.id}.')
                comment.delete()
            logger.debug(f'Comment#{comment.id}, karma:{comment.score} is above threshold of {limit}.')
            continue
    except praw.exceptions.PRAWException as err:
        logger.exception(f'check_comments: {err}')


def check_database()-> None:
    """Checks messages in database and sends PM if expiration time passed.

    Checks messages saved in a MySQL-compatible database and sends a reminder
    via PM if the expiration time has passed. If so, the message is removed from the
    database.

    Returns:
         None. Message is removed from database if expiration time has passed.
    """
    db.open_connections()
    # Get list of messages older than current datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    messages = db.get_messages(now)

    if not messages:
        logger.debug(f'No messages before: {now}.')
        db.close_connections()
        return None

    # Send reminder PM
    for message in messages:
        tid, link, msg, _exp, usr = message
        logger.debug(f'Found message: {tid}, {msg}')
        send_reminder(link, msg, usr)
        logger.info(f'Reminder sent: {link}.')

        # Delete message from database
        db.delete_message(tid)
        logger.info(f'Message deleted.')
    db.close_connections()


def send_reminder(link: str, msg: str, usr: str)-> None:
    """Sends reminder PM to username.

    Function sends given permalink and message to given username.

    Args:
         link:  Permalink to comment.
         msg:   Message in comment that was saved.
         usr:   User to send reminder to.

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


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
