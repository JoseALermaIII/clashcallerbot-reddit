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
import prawcore

import logging.config
import re
import datetime

import clashcallerbot_database as db

# Logger
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logging.raiseExceptions = True  # Production mode if False (no console sys.stderr output)
logger = logging.getLogger('search')

# Generate reddit instance
reddit = praw.Reddit('clashcaller')  # Section name in praw.ini
subreddit = reddit.subreddit('ClashCallerBot')  # Limit scope for testing purposes


def main():
    # Search recent comments for ClashCaller! string
    clashcaller_re = re.compile(r'''
                                [!|\s]?             # prefix ! or space (optional)
                                [C|c]lash[C|c]aller # upper or lowercase ClashCaller
                                [!|\s]              # suffix ! or space (required)
                                ''', re.VERBOSE)
    for comment in subreddit.stream.comments():
        match = clashcaller_re.search(comment.body)
        if match and comment.author.name != 'ClashCallerBot' \
                and not db.find_comment_id(comment.id) and not have_replied(comment.id, 'ClashCallerBot'):
            logger.info(f'In from {comment.author.name}: {comment}')
            # TODO: If found, parse username, comment date, message, permalink, and expiration time (if any)

            # Strip everything before and including ClashCaller! string
            comment.body = comment.body[match.end():].strip()
            logger.debug(f'Stripped comment body: {comment.body}')

            # Check for expiration time
            expiration_re = re.compile(r'''
                                       (?P<exp_digit>(\d){1,2})    # single or double digit
                                       (\s)?                       # optional space
                                       (?P<exp_unit>minute(s)?\s|  # minute(s) (space after required)
                                       min\s|                      # minute abbr. (space after required)
                                       hour(s)?\s|                 # hour(s) (space after required)
                                       hr\s                        # hour abbr. (space after required)
                                       )+''', re.VERBOSE | re.IGNORECASE)  # case-insensitive
            minute_tokens = ('min', 'minute', 'minutes')
            match = expiration_re.search(comment.body)
            if not match:
                timedelta = datetime.timedelta(hours=1)  # Default to 1 hour
            else:
                exp_digit = int(match.group('exp_digit').strip())
                if exp_digit == 0:  # ignore zeros
                    # Send message and ignore comment
                    error = 'Expiration time is zero.'
                    send_error_message(comment.author.id, error)
                    logging.error(error)
                    continue
                exp_unit = match.group('exp_unit').strip().lower()
                if exp_unit in minute_tokens:
                    timedelta = datetime.timedelta(minutes=exp_digit)
                else:
                    if exp_digit >= 24:  # ignore days
                        # Send message and ignore comment
                        error = 'Expiration time is >= 1 day.'
                        send_error_message(comment.author.id, error)
                        logging.error(error)
                        continue
                    # TODO: Ignore negative numbers
                    timedelta = datetime.timedelta(hours=exp_digit)
            logger.debug(f'timedelta = {timedelta.seconds} seconds')

            # Apply expiration time to comment date
            comment_datetime = datetime.datetime.fromtimestamp(comment.created_utc, datetime.timezone.utc)
            logger.info(f'comment_datetime = {comment_datetime}')
            expiration_datetime = comment_datetime + timedelta
            logger.info(f'expiration_datetime = {expiration_datetime}')

            # Ignore if expire time passed
            if expiration_datetime < datetime.datetime.now(datetime.timezone.utc):
                # Send message and ignore comment
                error = 'Expiration time has already passed.'
                send_error_message(comment.author.id, error)
                logging.error(error)
                continue

            # Strip expiration time
            comment.body = comment.body[match.end():].strip()

            # Evaluate message
            if len(comment.body) > 100:
                # Send message and ignore comment
                error = 'Message length > 100 characters.'
                send_error_message(comment.author.id, error)
                logger.error(error)
                continue
            message_re = re.compile(r'''
                                    (\s)*     # optional space
                                    base      # required string: base
                                    [\W|\s]*  # optional non-word character or space
                                    (\d){1,2} # required single or double digit
                                    ''', re.VERBOSE | re.IGNORECASE)  # case-insensitive
            match = message_re.search(comment.body)
            if not match:
                # Send message and ignore comment
                error = 'Message not properly formatted.'
                logger.error(error)
                send_error_message(comment.author.id, error)
                continue

            message = comment.body
            logger.debug(f'message = {message}')

            # Save message data to MySQL-compatible database
            db.save_message(comment.permalink, message, expiration_datetime, comment.author.id)

            # Reply and send PM
            send_confirmation(comment.author.id, comment.permalink, expiration_datetime)
            send_confirmation_reply(comment.id, comment.permalink, expiration_datetime)

    # TODO: Add comment.id to database


def send_confirmation(uid: str, link: str, exp: datetime.datetime) -> bool:
    """Send confirmation to reddit user.

    Function sends given user confirmation of given expiration time with given link.

    Args:
        uid:    userID of user.
        link:   Permalink of comment.
        exp:    Expiration datetime of call.

    Returns:
        True if successful, False otherwise.
    """
    subject = 'ClashCallerBot Confirmation Sent'
    permalink = 'https://np.reddit.com' + link  # Permalinks are missing prefix
    time = datetime.datetime.strftime(exp, '%b. %d, %Y at %I:%M:%S %p (%Z)')
    message = f"""ClashCallerBot here!  
              I will be messaging you on {time} (UTC) to remind you of [**this link.**]({permalink})

              Thank you for entrusting us with your warring needs,
              - ClashCallerBot

              [^(More info)](https://www.reddit.com/r/ClashCallerBot/comments/4e9vo7/clashcallerbot_info/)
              """
    try:
        reddit.redditor(uid).message(subject, message.replace('                  ', ''))

    except prawcore.exceptions as err:
        logger.error(f'send_confirmation: {err}')
        return False
    return True


def send_error_message(uid: str, error: str) -> bool:
    """Send error message to reddit user.

    Function sends given error to given user.

    Args:
        uid:      userID of user.
        error:    Error to send to user.

    Returns:
        True if successful, False otherwise.
    """
    subject = 'Unable to save call due to error.'
    message = f"""ClashCallerBot here!  
              I regret to inform you that I could not save your call because of:
              {error}.  
              Please delete your call to reduce spam and try again after making the
              above change.

              Thank you for entrusting us with your warring needs,
              - ClashCallerBot

              [^(More info)](https://www.reddit.com/r/ClashCallerBot/comments/4e9vo7/clashcallerbot_info/)
              """
    try:
        reddit.redditor(uid).message(subject, message.replace('                  ', ''))

    except prawcore.exceptions as err:
        logger.error(f'send_error_message: {err}')
        return False
    return True


def send_confirmation_reply(cid: str, link: str, exp: datetime.datetime) -> str:
    """Replies to a comment.

    Function replies to a given comment ID with a given message.

    Args:
        cid:    Comment ID to reply to.
        link:   Permalink of comment.
        exp:    Expiration datetime of call.

    Returns:
        comment_id: id of new comment if successful, None otherwise
    """
    permalink = 'https://np.reddit.com' + link  # Permalinks are missing prefix
    time = datetime.datetime.strftime(exp, '%b. %d, %Y at %I:%M:%S %p (%Z)')
    message = f"""ClashCallerBot here!  
                      I will be messaging you on {time} (UTC) to remind you of [**this link.**]({permalink})

                      Thank you for entrusting us with your warring needs!

                      [^(More info)](https://www.reddit.com/r/ClashCallerBot/comments/4e9vo7/clashcallerbot_info/)
                      """
    comment_id = None
    try:
        comment_obj = reddit.comment(id=cid)
        comment_id = comment_obj.reply(message.replace('                  ', ''))

    except prawcore.exceptions as err:
        logger.error(f'send_confirmation_reply: {err}')
    return comment_id


def have_replied(cid: str, bot_name: str) -> bool:
    """Checks if bot user has replied to a comment.

    Function checks reply authors for bot user.

    Args:
        cid:        Comment ID to get replies of.
        bot_name:   Name of bot to check for.

    Returns:
        True if successful, False otherwise.
    """
    try:
        replies = reddit.comment(id=cid).replies

        if not replies:
            return False

        for reply in replies:
            if reply.author.name == bot_name:
                return True

    except prawcore.exceptions as err:
        logger.error(f'have_replied: {err}')
        return False
    return False


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
