#!/usr/bin/env python2.7

# =============================================================================
# IMPORTS
# =============================================================================

import praw
import OAuth2Util
import MySQLdb
import ConfigParser
import time
import logging
import logging.config
from datetime import datetime
from requests.exceptions import HTTPError, ConnectionError, Timeout
from praw.errors import APIException, InvalidUser, RateLimitExceeded
from socket import timeout
from pytz import timezone

# =============================================================================
# GLOBALS
# =============================================================================

# Reads the config file
config = ConfigParser.ConfigParser()
config.read("clashcallerbot.cfg")

# Reddit info
reddit = praw.Reddit("ClashCallerB0t Reply: v0.1")
o = OAuth2Util.OAuth2Util(reddit, print_log=True)
o.refresh(force=True)
# DB Info
DB_USER = config.get("SQL", "user")
DB_PASS = config.get("SQL", "passwd")
DB_NAME = config.get("SQL", "name")

# Logger
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logging.raiseExceptions = False # Production mode
logger = logging.getLogger('reply')


# =============================================================================
# CLASSES
# =============================================================================


class Connect(object):
    """
    DB connection class
    """
    connection = None
    cursor = None

    def __init__(self):
        self.connection = MySQLdb.connect(
            host="localhost", user=DB_USER, passwd=DB_PASS, db=DB_NAME
        )
        self.cursor = self.connection.cursor()


class Reply(object):
    def __init__(self):
        self._queryDB = Connect()
        self._replyMessage = (
            "ClashCallerBot private message here!"
            "\n\n**The message:** \n\n>{message}"
            "\n\n**The original comment:** \n\n>{original}"
            "\n\n**The parent comment from the original comment or its submission:** \n\n>{parent}"
            "\n\n_____\n\n"
            "|[^([FAQs])](https://www.reddit.com/r/ClashCallerBot/comments/4e9vo7/clashcallerbot_info/)"
            "|[^([Your Calls])](http://www.reddit.com/message/compose/?to=ClashCallerBot&subject=List Of Calls&message=MyCalls!)"
            "|[^([Feedback])](http://www.reddit.com/message/compose/?to=ClashCallerBotDbuggr&subject=ClashCallerBot Feedback)"
            "|[^([Code])](https://github.com/JoseALermaIII/clashcallerbot-reddit)"
            "\n|-|-|-|-|-|"
        )

    def parent_comment(self, dbPermalink):
        """
        Returns the parent comment or if it's a top comment
        return the original submission
        """
        try:
            commentObj = reddit.get_submission(_force_utf8(dbPermalink)).comments[0]
            if commentObj.is_root:
                return _force_utf8(commentObj.submission.permalink)
            else:
                return _force_utf8(reddit.get_info(thing_id=commentObj.parent_id).permalink)
        except IndexError:
            logger.exception("parent_comment error")
            return "It seems your original comment was deleted, unable to return parent comment."
        # Catch any URLs that are not reddit comments
        except Exception:
            logger.exception("HTTPError/PRAW parent comment")
            return "Parent comment not required for this URL."

    def time_to_reply(self):
        """
        Checks to see through SQL if new_date is < current time
        """

        # get current time to compare
        currentTime = datetime.now(timezone('UTC'))
        currentTime = format(currentTime, '%Y-%m-%d %H:%M:%S')
        cmd = "SELECT * FROM message_date WHERE new_date < %s"
        self._queryDB.cursor.execute(cmd, [currentTime])

    def search_db(self):
        """
        Loop through data looking for which comments are old
        """

        data = self._queryDB.cursor.fetchall()
        alreadyCommented = []
        for row in data:
            # checks to make sure ID hasn't been commented already
            # For situtations where errors happened
            if row[0] not in alreadyCommented:
                flagDelete = False
                # MySQl- permalink, message, reddit user
                flagDelete = self.new_reply(row[1], row[2], row[4])
                # removes row based on flagDelete
                if flagDelete:
                    cmd = "DELETE FROM message_date WHERE id = %s"
                    self._queryDB.cursor.execute(cmd, [row[0]])
                    self._queryDB.connection.commit()
                    alreadyCommented.append(row[0])

        self._queryDB.connection.commit()
        self._queryDB.connection.close()

    def new_reply(self, permalink, message, author):
        """
        Replies a second time to the user after a set amount of time
        """
        """
        print self._replyMessage.format(
                message,
                permalink
            )
        """
        logger.info("---------------")
        logger.info(str(author))
        logger.info(str(permalink))
        try:
            reddit.send_message(
                recipient=str(author),
                subject='Hello, ' + _force_utf8(str(author)) + ' ClashCallerBot Here!',
                message=self._replyMessage.format(
                    message=_force_utf8(message),
                    original=_force_utf8(permalink),
                    parent=self.parent_comment(permalink)
                ))
            logger.info("Did It")
            return True
        except InvalidUser:
            logger.exception("InvalidUser")
            return True
        except APIException:
            logger.exception("APIException")
            return False
        except IndexError:
            logger.exception("IndexError")
            return False
        except (HTTPError, ConnectionError, Timeout, timeout):
            logger.exception("HTTPError")
            time.sleep(10)
            return False
        except RateLimitExceeded:
            logger.exception("RateLimitExceeded")
            time.sleep(10)
            return False
        except praw.errors.HTTPException:
            logger.exception("praw.errors.HTTPException")
            time.sleep(10)
            return False


"""
From Reddit's Code 
https://github.com/reddit/reddit/blob/master/r2/r2/lib/unicode.py
Brought to attention thanks to /u/13steinj
"""


def _force_unicode(text):
    if text is None:
        return u''

    if isinstance(text, unicode):
        return text

    try:
        text = unicode(text, 'utf-8')
    except UnicodeDecodeError:
        text = unicode(text, 'latin1')
    except TypeError:
        text = unicode(text)
    return text


def _force_utf8(text):
    return str(_force_unicode(text).encode('utf8'))


# =============================================================================
# MAIN
# =============================================================================

def main():

    while True:
        checkReply = Reply()
        checkReply.time_to_reply()
        checkReply.search_db()
        time.sleep(10)


# =============================================================================
# RUNNER
# =============================================================================
logger.info('Start')
if __name__ == '__main__':
    main()
