#! python3
# -*- coding: utf-8 -*-
"""Searches recent reddit comments for ClashCaller! string and saves to database.

This module uses the Python Reddit API Wrapper (PRAW) to search recent reddit comments
for the ClashCaller! string.

If found, the userID, permalink, comment time, message, and
expiration time (if any) are parsed. The default, or provided, expiration time is
applied, then all the comment data is saved to a MySQL-compatible database.

The comment is replied to, then the userID is PM'ed confirmation."""

import praw
import praw.exceptions
import prawcore.exceptions

import logging.config
import re
import datetime
import time
import urllib3.exceptions
from socket import gaierror

from clashcallerbotreddit.database import ClashCallerDatabase
from clashcallerbotreddit import LOGGING, config

# Logger
logging.config.dictConfig(LOGGING)
# FIXME: logging.raiseExceptions = False crashes during exception. Maybe remove console handler?
logging.raiseExceptions = True  # Production mode if False (no console sys.stderr output)
logger = logging.getLogger('search')

# Generate reddit instance
reddit = praw.Reddit('clashcallersearch')  # Section name in praw.ini
#subreddit = reddit.subreddit('ClashCallerBot')  # Limit scope for testing purposes
subreddit = reddit.subreddit('all')  # Production mode
reddituser = reddit.user.me()

# Regular expressions
clashcaller_re = re.compile(r'''
                            [!|\s]?             # prefix ! or space (optional)
                            [C|c]lash[C|c]aller # lower or camelcase ClashCaller (required)
                            [!|\s]              # suffix ! or space (required)
                            ''', re.VERBOSE)
expiration_re = re.compile(r'''
                           (?P<exp_digit>(\d){1,2})    # single or double digit (required)
                           (\s)?                       # space (optional)
                           (?P<exp_unit>minute(s)?\s|  # minute(s) (space after required)
                           min(s)?\s|                  # minute abbr. (space after required)
                           hour(s)?\s|                 # hour(s) (space after required)
                           hr(s)?\s                    # hour abbr. (space after required)
                           )+''', re.VERBOSE | re.IGNORECASE)  # case-insensitive
message_re = re.compile(r'''
                        (\s)*       # space (optional)
                        "           # opening double quote (required)
                        base(s)?    # string: base(s) (required)
                        [\W|\s]*    # non-word character or space (optional)
                        (\d){1,2}   # single or double digit (required)
                        .*          # any character after (optional)
                        "           # closing double quote (required)
                        ''', re.VERBOSE | re.IGNORECASE)  # case-insensitive

# Make database instance
db = ClashCallerDatabase(config, root_user=False)

start_time = datetime.datetime.now(datetime.timezone.utc)


def main():
    logger.info('Start search.py...')
    while True:
        try:
            # Search recent comments for ClashCaller! string
            for comment in subreddit.stream.comments():
                match = clashcaller_re.search(comment.body)
                if not match:
                    # Skip comments that don't have the clashcaller string
                    continue
                if not is_recent(comment.created_utc, start_time):
                    # Skip comments that are before start_time
                    continue
                if comment.author.name == reddituser.name:
                    # Skip bot's comments
                    continue
                if have_replied(comment, reddituser.name):
                    # Skip comments already replied to
                    logger.debug(f'Skipping {comment}: already replied.')
                    continue
                logger.info(f'In: {comment}')

                # Strip everything before and including ClashCaller! string
                comment.body = comment.body[match.end():].strip()
                logger.debug(f'Stripped comment body: {comment.body}')

                # Check for expiration time
                minute_tokens = ('min', 'mins', 'minute', 'minutes')
                match = expiration_re.search(comment.body)
                if not match:
                    timedelta = datetime.timedelta(hours=1)  # Default to 1 hour
                else:
                    exp_digit = int(match.group('exp_digit').strip())
                    if exp_digit == 0:  # ignore zeros
                        # Send message and ignore comment
                        error = 'Expiration time is zero.'
                        # send_error_message(comment.author.name, comment.permalink, error)
                        logging.error(error)
                        continue
                    exp_unit = match.group('exp_unit').strip().lower()
                    if exp_unit in minute_tokens:
                        timedelta = datetime.timedelta(minutes=exp_digit)
                    else:
                        if exp_digit >= 24:  # ignore days
                            # Send message and ignore comment
                            error = 'Expiration time is >= 1 day.'
                            # send_error_message(comment.author.name, comment.permalink, error)
                            logging.error(error)
                            continue
                        timedelta = datetime.timedelta(hours=exp_digit)
                logger.debug(f'timedelta = {timedelta.seconds} seconds')

                # Apply expiration time to comment date
                comment_datetime = datetime.datetime.fromtimestamp(comment.created_utc, datetime.timezone.utc)
                expiration_datetime = comment_datetime + timedelta
                logger.info(f'comment_datetime = {comment_datetime}')
                logger.info(f'expiration_datetime = {expiration_datetime}')

                # Ignore if expire time passed
                if expiration_datetime < datetime.datetime.now(datetime.timezone.utc):
                    # Send message and ignore comment
                    error = 'Expiration time has already passed.'
                    # send_error_message(comment.author.name, comment.permalink, error)
                    logging.error(error)
                    continue

                # Strip expiration time
                comment.body = comment.body[match.end():].strip()

                # Evaluate message
                if len(comment.body) > 100:
                    # Send message and ignore comment
                    error = 'Message length > 100 characters.'
                    # send_error_message(comment.author.name, comment.permalink, error)
                    logger.error(error)
                    continue

                match = message_re.search(comment.body)
                if not match:
                    # Send message and ignore comment
                    error = 'Message not properly formatted.'
                    # send_error_message(comment.author.name, comment.permalink, error)
                    logger.error(error)
                    continue

                message = comment.body
                logger.debug(f'message = {message}')

                # Save message data to MySQL-compatible database
                db.open_connections()
                db.save_message(comment.permalink, message, expiration_datetime, comment.author.name)
                db.close_connections()

                # Reply and send PM
                send_confirmation(comment.author.name, comment.permalink, expiration_datetime)
                send_confirmation_reply(comment, expiration_datetime, message)

        except urllib3.exceptions.ConnectionError as err:
            logger.exception(f'urllib3: {err}')
            time.sleep(20)
            pass

        except gaierror as err:
            logger.exception(f'socket: {err}')
            time.sleep(20)
            pass

        except prawcore.exceptions.PrawcoreException as err:
            logger.exception(f'prawcore: {err}')
            time.sleep(60)
            pass

        except praw.exceptions.PRAWException as err:
            logger.exception(f'praw: {err}')
            time.sleep(10)
            pass

        except AttributeError as err:
            logger.exception(f'AttributeError: {err}')
            time.sleep(10)
            pass


def send_message(usr_name: str, subject_arg: str, message_arg: str) -> None:
    """Send message to reddit user.

    Sends a message to a reddit user with given subject line.

    Args:
         usr_name: username of user.
         subject_arg: Subject line of message.
         message_arg: Message to send.

    Returns:
        None.
    """
    try:
        reddit.redditor(usr_name).message(subject_arg, message_arg)

    except praw.exceptions.PRAWException as err:
        logger.exception(f'send_message: {err}')


def send_confirmation(usr_name: str, link: str, exp: datetime.datetime) -> None:
    """Send confirmation to reddit user.

    Function sends given user confirmation of given expiration time with given link.

    Args:
        usr_name: username of user.
        link:   Permalink of comment.
        exp:    Expiration datetime of call.

    Returns:
        None.
    """
    subject = f'{reddituser.name} Confirmation Sent'
    permalink = 'https://np.reddit.com' + link  # Permalinks are missing prefix
    exp = datetime.datetime.strftime(exp, '%b. %d, %Y at %I:%M:%S %p %Z')
    message = f"""{reddituser.name} here!  
I will be messaging you on [**{exp}**](http://www.wolframalpha.com/input/?i={exp} To Local Time) to remind 
you of [**this call.**]({permalink})

Thank you for entrusting us with your warring needs,  
- {reddituser.name}

[^(More info)](https://www.reddit.com/r/{reddituser.name}/comments/4e9vo7/clashcallerbot_info/)
              """
    try:
        send_message(usr_name, subject, message)

    except praw.exceptions.PRAWException as err:
        logger.exception(f'send_confirmation: {err}')


def send_error_message(usr_name: str, link: str, error: str) -> None:
    """Send error message to reddit user.

    Function sends given error to given user.

    Args:
        usr_name:   username of user.
        link:     Permalink of comment.
        error:    Error to send to user.

    Returns:
        None.
    """
    subject = 'Unable to save call due to error'
    permalink = 'https://np.reddit.com' + link  # Permalinks are missing prefix
    message = f"""{reddituser.name} here!  
I regret to inform you that I could not save [**your call**]({permalink}) because of:
{error}  
Please delete your call to reduce spam and try again after making the
above change.

Thank you for entrusting us with your warring needs,  
- {reddituser.name}

[^(More info)](https://www.reddit.com/r/{reddituser.name}/comments/4e9vo7/clashcallerbot_info/)
              """
    try:
        send_message(usr_name, subject, message)

    except praw.exceptions.PRAWException as err:
        logger.exception(f'send_error_message: {err}')


def send_confirmation_reply(cmnt_obj: reddit.comment, exp: datetime.datetime, message_arg: str):
    """Replies to a comment.

    Function replies to a given comment object with a given message.

    Args:
        cmnt_obj: Comment object to reply to.
        exp:    Expiration datetime of call.
        message_arg: Original call message.

    Returns:
        id of new comment if successful, None otherwise
    """
    link = cmnt_obj.permalink
    permalink = 'https://np.reddit.com' + link  # Permalinks are missing prefix
    pretty_exp = datetime.datetime.strftime(exp, '%b. %d, %Y at %I:%M:%S %p %Z')  # Human readable datetime
    message = f"""
I will be messaging you on [**{pretty_exp}**](http://www.wolframalpha.com/input/?i={pretty_exp} To Local Time) 
to remind you of [**this call.**]({permalink})

Others can tap
[**REMIND ME, TOO**](https://www.reddit.com/message/compose/?to={reddituser.name}&subject=AddMe!&message=[{link}]{exp}{message_arg}) 
to send me a PM to be added to the call reminder and reduce spam.

You can also tap 
[**REMOVE ME**](https://www.reddit.com/message/compose/?to={reddituser.name}&subject=DeleteMe!&message=[{link}]) to 
remove yourself from the call reminder or
[**MY CALLS**](https://www.reddit.com/message/compose/?to={reddituser.name}&subject=MyCalls!&message=El Zilcho) 
to list your current calls.

Thank you for entrusting us with your warring needs!
 
[^(More info)](https://www.reddit.com/r/{reddituser.name}/comments/4e9vo7/clashcallerbot_info/)
              """
    comment_id = None
    try:
        comment_id = cmnt_obj.reply(message)

    except praw.exceptions.PRAWException as err:
        logger.exception(f'send_confirmation_reply: {err}')
    return comment_id


def have_replied(cmnt_obj: reddit.comment, usr_name: str) -> bool:
    """Check if user has replied to a comment.

    Function checks reply authors of given comment for given user.

    Args:
        cmnt_obj:   Comment object to get replies of.
        usr_name:   Name of bot to check for.

    Returns:
        True if successful, False otherwise.
    """
    try:
        cmnt_obj.refresh()  # Refreshes attributes of comment to load replies

        # Keep fetching 20 new replies until it finishes
        while True:
            try:
                replies = cmnt_obj.replies.replace_more()
                break
            except praw.exceptions.PRAWException as err:
                logger.exception(f'comment.replies.replace_more: {err}')
                time.sleep(1)

        if not replies:
            return False

        for reply in replies:
            if reply.author.name == usr_name:
                return True

    except praw.exceptions.PRAWException as err:
        logger.exception(f'have_replied: {err}')
    return False


def is_recent(cmnt_time: float, time_arg: datetime.datetime) -> bool:
    """Checks if comment is a recent comment.

    Function compares given comment Unix timestamp with given time.

    Args:
        cmnt_time:  Comment's created Unix timestamp in UTC.
        time_arg: Time to compare with comment timestamp.

    Returns:
        True if comment's created time is after given time, False otherwise.
    """
    cmnt_datetime = datetime.datetime.fromtimestamp(cmnt_time, datetime.timezone.utc)
    if cmnt_datetime > time_arg:
        return True
    return False


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
