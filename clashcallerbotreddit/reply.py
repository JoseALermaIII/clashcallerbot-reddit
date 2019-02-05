#! python3
# -*- coding: utf-8 -*-
"""Performs cleanup operations.

This module implements functions designed to clean up various data sets:

* Sends and deletes stored messages in the MySQL-compatible database.
* Checks bot's comments and removes comments below a certain threshold.
* Checks bot's messages for keywords and deletes them after:

    * Adding message author to call reminder.
    * PMing list of message author's calls.
    * Deleting message author from call.

"""

import praw
import praw.exceptions

import logging.config
import re
import datetime
import time

from clashcallerbotreddit.database import ClashCallerDatabase
from clashcallerbotreddit.search import is_recent, message_re, send_message
from clashcallerbotreddit import LOGGING, config

# Logger
logging.config.dictConfig(LOGGING)
# FIXME: logging.raiseExceptions = False crashes during exception. Maybe remove console handler?
logging.raiseExceptions = True  # Production mode if False (no console sys.stderr output)
logger = logging.getLogger('reply')

# Generate reddit instance
reddit = praw.Reddit('clashcallerreply')  # Section name in praw.ini
#subreddit = reddit.subreddit('ClashCallerBot')  # Limit scope for testing purposes
subreddit = reddit.subreddit('all')  # Production mode
reddituser = reddit.user.me()

# Make database instance
db = ClashCallerDatabase(config, root_user=False)

# Time constants
start_time = datetime.datetime.now(datetime.timezone.utc)
archive_time = start_time - datetime.timedelta(weeks=12)  # 6 months archival time

# Regular expressions
addme_re = re.compile(r'''
                        \[              # opening square bracket (required)
                        (?P<link_re>
                        (\S)+)          # any non-whitespace characters (required)
                        \]              # closing square bracket (required)
                        (?P<exp_re> 
                        (\d){4}-        # four digit number followed by hyphen (required)
                        (\d){1,2}-      # one or two digit number followed by hyphen (required)
                        (\d){1,2}\s     # one or two digit number followed by space (required)
                        ((\d){2}:){2}   # two, two digit numbers followed by a colon (required)
                        (\d){2})        # two digit number followed (required)
                        ''', re.VERBOSE)

delete_re = re.compile(r'''
                        ^               # beginning of string
                        \[              # opening square bracket (required)
                        (?P<link_re>
                        (\S)+)          # any non-whitespace characters (required)
                        \]              # closing square bracket (required)
                        (\s)*           # one or more spaces (optional)
                        $               # end of string
                        ''', re.VERBOSE)

# Call table spacers
spacers = {'left': '| ', 'mid': ' | ', 'right': ' |'}


def main():
    logger.info('Start reply.py...')
    while True:
        time.sleep(120)  # 2 minutes

        # Check saved messages
        check_database()

        # Check for comments below threshold
        check_comments(reddituser.name)

        # Check messages for tasks
        check_messages()


def check_messages()-> None:
    """Checks inbox messages.

    Checks authorized user's inbox messages for commands, processes them, then deletes the message.

    Returns:
        None. Messages are processed then deleted.

    Notes:
        * Does not process mentions or comment replies.
        * Skips old messages (> 6 months from start time).

    """
    try:
        # Fetch as many messages as possible
        messages = reddit.inbox.messages(limit=None)
        for message in messages:
            # Skip sent messages
            if message.author.name == reddituser.name:
                #logger.debug(f'Inbox skip sent message: {message.id}.')
                continue
            # Skip old messages
            if not is_recent(message.created_utc, archive_time):
                #logger.debug(f'Inbox skip old message: {message.id}.')
                continue
            # Process list command
            if message.subject == 'MyCalls!':
                logger.info(f'Inbox list: {message.id}.')
                process_my_calls(message)
            # Process add command
            elif message.subject == 'AddMe!':
                logger.info(f'Inbox add: {message.id}.')
                process_add_me(message)
            # Process delete command
            elif message.subject == 'DeleteMe!':
                logger.info(f'Inbox delete: {message.id}.')
                process_delete_me(message)
            # Process everything else
            else:
                logger.exception(f'Inbox uncaught command: {message.subject}.\n'
                                 f'Message: {message.body}.')
                message.delete()

    except praw.exceptions.PRAWException as err:
        logger.exception(f'check_messages: {err}')


def process_add_me(msg_obj: praw.reddit.models.Message):
    """Process an AddMe! command from a message.

    Processes an AddMe! command from a given message that invoked it. The message author is added to the
    MySQL-compatible database with the permalink, message, and expiration time from the message body.

    Args:
        msg_obj: Instance of Message class that invoked the AddMe! command.

    Returns:
        Error message string if unsuccessful, None otherwise.

    """
    # Get URL and expiration time from message body
    match = addme_re.search(msg_obj.body)
    if not match:
        err = f'Inbox skip add (bad message format): {msg_obj.id}.'
        logger.debug(err)
        msg_obj.delete()
        return err
    link_re = match.group('link_re')
    # Check if call already in db
    db.open_connections()
    user_calls = db.get_removable_messages(msg_obj.author.name, link_re)
    if user_calls:
        err = f'Inbox skip add (call already in db): {msg_obj.id}.'
        logger.debug(err)
        msg_obj.delete()
        db.close_connections()
        return err
    exp_re = match.group('exp_re')
    exp_re += '+0000'  # add UTC offset
    exp_datetime = datetime.datetime.strptime(exp_re, '%Y-%m-%d %H:%M:%S%z')  # Convert to MySQL datetime object
    now = datetime.datetime.now(datetime.timezone.utc)
    logger.info(f'Comment link: {link_re}.')
    logger.info(f'Expiration datetime: {exp_datetime}.')
    if now > exp_datetime:
        err = f'Inbox skip add (expired message): {msg_obj.id}.'
        logger.debug(err)
        msg_obj.delete()
        return err
    # Get call message from message body
    match = message_re.search(msg_obj.body)
    if not match:
        err = f'Inbox skip add (bad call message format): {msg_obj.id}.'
        logger.debug(err)
        msg_obj.delete()
        return err
    call_message = match.group(0)
    # Add to database
    logger.info(f'Inbox add save to db: {msg_obj.id}.')
    db.save_message(link_re, call_message, exp_datetime, msg_obj.author.name)
    db.close_connections()
    # Delete message
    msg_obj.delete()


def process_delete_me(msg_obj: praw.reddit.models.Message):
    """Process a DeleteMe! command from a message.

    Processes a DeleteMe! command from a given message that invoked it. If calls from the message author for the
    permalink from the message body are found in the MySQL-compatible database, they are removed from the database.

    Args:
        msg_obj: Instance of Message class that invoked the DeleteMe! command.

    Returns:
        Error message string if unsuccessful, None otherwise.

    """
    # Get URL from message body
    match = delete_re.search(msg_obj.body)
    if not match:
        err = f'Inbox skip delete: {msg_obj.id}.'
        logger.debug(err)
        msg_obj.delete()
        return err
    link_re = match.group('link_re')
    # Check database for matching rows
    db.open_connections()
    deletable_messages = db.get_removable_messages(msg_obj.author.name, link_re)
    if not deletable_messages:
        err = f'Inbox skip delete (no deletable_messages): {msg_obj.id}.'
        logger.debug(err)
        msg_obj.delete()
        return err
    # Delete matching rows
    for deletable_message in deletable_messages:
        tid, link_saved, _msg, _exp, _usr = deletable_message
        db.delete_row(tid)
        logger.info(f'Inbox delete message deleted: {link_saved}.')
    db.close_connections()
    # Delete message
    msg_obj.delete()


def process_my_calls(msg_obj: praw.reddit.models.Message):
    """Process a MyCalls! command from a message.

    Processes a MyCalls! command from a given message that invoked it. If calls from the message author are found in
    the MySQL-compatible database, they are sent in a table format via PM.

    Args:
        msg_obj: Instance of Message class that invoked the MyCalls! command.

    Returns:
        Error message string if unsuccessful, None otherwise.

    """
    # Check database for user's calls
    db.open_connections()
    current_calls = db.get_user_messages(msg_obj.author.name)
    db.close_connections()
    if not current_calls:
        err = f'Inbox skip list (no current_calls): {msg_obj.id}.'
        logger.debug(err)
        msg_obj.delete()
        return err
    # Display calls, if found
    call_table = [
        (spacers['left'], 'Permalink', spacers['mid'], 'Call Message', spacers['mid'], 'Expiration',
         spacers['right']),
        ('|', ':-:', '|', ':-:', '|', ':-:', '|')
    ]
    for call in current_calls:
        _tid, link_saved, msg_saved, exp_saved, _usr = call
        exp_saved = datetime.datetime.strftime(exp_saved,
                                               '%b. %d, %Y at %I:%M:%S %p UTC')  # Human readable datetime
        link_saved = '\\' + link_saved  # escape reddit markdown syntax
        table_row = (spacers['left'], link_saved, spacers['mid'], msg_saved, spacers['mid'],
                     f'[**{exp_saved}**](http://www.wolframalpha.com/input/?i={exp_saved} To Local Time)',
                     spacers['right'])
        call_table.append(table_row)
    call_table_string = '\n'.join(''.join(element for element in row) for row in call_table)
    calls_message = f"""ClashCallerBot here!  
Your current calls are as follows:

{call_table_string}

If you wish to delete a call, copy the entry in the permalink column and paste it between the brackets in 
[**THIS PM**](https://www.reddit.com/message/compose/?to=ClashCallerBot&subject=DeleteMe!&message=[PASTE_HERE]).

Thank you for entrusting us with your warring needs,  
- ClashCallerBot
                    """
    send_message(msg_obj.author, f'{reddituser.name} List Calls', calls_message)
    logger.info(f'Inbox list calls list sent: {msg_obj.id}.')
    # Delete message
    msg_obj.delete()


def check_comments(usr: str, limit: int = -5)-> None:
    """Checks comments and deletes if at or below threshold.

    Checks given user's last 100 comments and deletes each one at or below the given threshold.

    Args:
        usr: User to check comments of.
        limit: Threshold at or below which comment will be deleted. Defaults to ``-5``.

    Returns:
         None. Comments at or below threshold are deleted.

    Note:
        Skips archived comments (> 6 months from start time).

    """
    try:
        comments = reddit.redditor(usr).comments.new()
        for comment in comments:
            if not is_recent(comment.created_utc, archive_time):
                logger.info(f'Skipping comments after {archive_time}.')
                return None

            if comment.score <= limit:
                logger.info(f'Deleting comment at or below threshold of {limit}: {comment.id}.')
                comment.delete()
            #logger.debug(f'Comment# {comment.id}, karma:{comment.score} is above threshold of {limit}.')
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
    messages = db.get_expired_messages(now)

    if not messages:
        #logger.debug(f'No messages before: {now}.')
        db.close_connections()
        return None

    # Send reminder PM
    for message in messages:
        tid, link, msg, _exp, usr = message
        logger.debug(f'Found message: {tid}, {msg}')
        send_reminder(link, msg, usr)
        logger.info(f'Reminder sent: {link}.')

        # Delete message from database
        db.delete_row(tid)
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
        send_message(usr, subject, message)

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
