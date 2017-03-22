#!/usr/bin/env python2.7

# =============================================================================
# IMPORTS
# =============================================================================
import traceback
import praw
import OAuth2Util
import re
import MySQLdb
import ConfigParser
import ast
import time
import urllib
import requests
import parsedatetime.parsedatetime as pdt
import logging
import logging.config
from datetime import datetime
from praw.exceptions import APIException
from praw.models import Message, Comment
from prawcore import Forbidden
from pytz import timezone
from threading import Thread

# =============================================================================
# GLOBALS
# =============================================================================

# Reads the config file
config = ConfigParser.ConfigParser()
config.read("praw.ini")

# Reddit info
reddit = praw.Reddit("Reddit",
                     user_agent="Python:ClashCallerB0tSearch:v1.0 (by /u/ClashCallerBotDbuggr)")
#o = OAuth2Util.OAuth2Util(reddit, print_log=True)
#o.refresh(force=True)

DB_USER = config.get("SQL", "user")
DB_PASS = config.get("SQL", "passwd")
DB_NAME = config.get("SQL", "name")

# Time when program was started
START_TIME = time.time()

# Logger
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logging.raiseExceptions = False  # Production mode
logger = logging.getLogger('search')


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


class Search(object):
    commented = []  # comments already replied to

    # Fills subId with previous threads. Helpful for restarts
    database = Connect()
    cmd = "SELECT list FROM comment_list WHERE id = 1"
    database.cursor.execute(cmd)
    data = database.cursor.fetchall()
    subId = ast.literal_eval("[" + data[0][0] + "]")  # reddit threads already replied in
    database.connection.commit()
    database.connection.close()

    endMessage = (
        "\n\n_____\n\n"
        "|[^([FAQs])](https://www.reddit.com/r/ClashCallerBot/comments/4e9vo7/clashcallerbot_info/)"
        "|[^([Your Calls])](http://www.reddit.com/message/compose/?to=ClashCallerBot"
        "&subject=List Of Calls&message=MyCalls!)"
        "|[^([Feedback])](http://www.reddit.com/message/compose/?to=ClashCallerBotDbuggr"
        "&subject=ClashCallerBot Feedback)"
        "|[^([Code])](https://github.com/JoseALermaIII/clashcallerbot-reddit)"
        "\n|-|-|-|-|-|"
    )

    def __init__(self, comment):
        self._addToDB = Connect()
        self.comment = comment  # reddit comment Object
        self._messageInput = '"Hello, I\'m here to remind you to see the parent comment!"'
        self._storeTime = None
        self._replyMessage = ""
        self._replyDate = None
        self._privateMessage = False

    def run(self, privateMessage=False):
        self._privateMessage = privateMessage
        self.parse_comment()
        self.save_to_db()
        self.build_message()
        self.reply()
        if self._privateMessage:
            # Makes sure to marks as read, even if the above doesn't work
            self.comment.mark_as_read()
            self.find_bot_child_comment()
        self._addToDB.connection.close()

    def parse_comment(self):
        """
        Parse comment looking for the message and time
        """

        if self._privateMessage:
            permalinkTemp = re.search('\[(.*?)\]', self.comment.body)
            if permalinkTemp:
                self.comment.permalink = permalinkTemp.group()[1:-1]
                # Makes sure the URL is real
                try:
                    urllib.urlopen(self.comment.permalink)
                except IOError:
                    self.comment.permalink = "https://www.reddit.com/r/ClashCallerBot/comments/" \
                                             "4e9vo7/clashcallerbot_info/"
            else:
                # Defaults when the user doesn't provide a link
                self.comment.permalink = "https://www.reddit.com/r/ClashCallerBot/comments/" \
                                         "4e9vo7/clashcallerbot_info/"

        # remove ClashCaller! or !ClashCaller (case insensitive)
        match = re.search(r'(?i)(!*)ClashCaller(!*)', self.comment.body)
        # and everything before
        tempString = self.comment.body[match.start():]

        # remove all format breaking characters IE: [ ] ( ) newline
        tempString = tempString.split("\n")[0]
        # adds " at the end if only 1 exists
        if (tempString.count('"') == 1):
            tempString += '"'

        # Checks for message
        messageInputTemp = re.search('(["].{0,9000}["])', tempString)
        if messageInputTemp is None:
            reddit.redditor(self.comment.author).message('Hello, ' + str(self.comment.author) + ' no message was inlcuded',
                                "A message is required.\n\n Go to https://www.reddit.com/r/ClashCallerBot/comments/"
                                "4e9vo7/clashcallerbot_info for usage.")
            self.commented.append(self.comment.id)  # Add to handled comments.
            logger.exception('No Message from %s', self.comment.author)
            raise Exception('No Message')
        else:
            self._messageInput = messageInputTemp.group()

        # Fix issue with dashes for parsedatetime lib
        tempString = tempString.replace('-', "/")
        # Remove ClashCaller!
        self._storeTime = re.sub('(["].{0,9000}["])', '', tempString)[9:]

    def save_to_db(self):
        """
        Saves the permalink comment, the time, and the message to the DB
        """

        cal = pdt.Calendar()
        holdTime = cal.parse(self._storeTime, datetime.now(timezone('UTC')))
        if holdTime[1] == 0:
            # default time
            holdTime = cal.parse("1 hour", datetime.now(timezone('UTC')))
            self._replyMessage = "**Defaulted to one hour.**\n\n"
        # Converting time
        # 9999/12/31 HH/MM/SS
        self._replyDate = time.strftime('%Y-%m-%d %H:%M:%S', holdTime[0])
        cmd = "INSERT INTO message_date (permalink, message, new_date, userID) VALUES (%s, %s, %s, %s)"
        self._addToDB.cursor.execute(cmd, (
            self.comment.permalink.encode('utf-8'),
            self._messageInput.encode('utf-8'),
            self._replyDate,
            self.comment.author))
        self._addToDB.connection.commit()
        # Info is added to DB, user won't be bothered a second time
        self.commented.append(self.comment.id)

    def build_message(self):
        """
        Building message for user
        """
        permalink = self.comment.permalink
        self._replyMessage += (
            "I will be messaging you on [**{0} UTC**](http://www.wolframalpha.com/input/?i={0} UTC To Local Time)"
            " to remind you of [**this link.**]({commentPermalink})"
            "{clashCallMessage}")

        try:
            self.sub = reddit.submission(url=self.comment.permalink)
        except Exception:
            logger.exception("link had http")
        if self._privateMessage == False and self.sub.id not in self.subId:
            clashCallMessage = (
                "\n\n^(Parent commenter can ) [^(delete this message to hide from others.)]"
                "(http://www.reddit.com/message/compose/?to=ClashCallerBot"
                "&subject=Delete Comment&message=Delete! ____id____)").format(
                permalink=permalink,
                time=self._storeTime.replace('\n', '')
            )
        else:
            clashCallMessage = ""

        self._replyMessage = self._replyMessage.format(
            self._replyDate,
            clashCallMessage=clashCallMessage,
            commentPermalink=permalink)
        self._replyMessage += Search.endMessage

    def reply(self):
        """
        Messages the user as a confirmation
        """

        author = self.comment.author

        def send_message():
            reddit.redditor(str(author)).message('Hello, ' + str(author) + ' ClashCallerBot Confirmation Sent',
                                self._replyMessage)

        try:
            if not self._privateMessage:
                # Messages will be a reply in a thread
                # identical messages are PM in the same thread
                newcomment = self.comment.reply(self._replyMessage)
                if (self.sub.id not in self.subId):
                    self.subId.append(self.sub.id)
                    # adding it to database as well
                    database = Connect()
                    insertsubid = ", \'" + self.sub.id + "\'"
                    cmd = 'UPDATE comment_list set list = CONCAT(list, "{0}") where id = 1'.format(insertsubid)
                    database.cursor.execute(cmd)
                    database.connection.commit()
                    database.connection.close()
                    # grabbing comment just made
                    reddit.comment(
                        id=str(newcomment.id)
                        #thing_id='t1_' + str(newcomment.id)
                        # edit comment with self ID so it can be deleted
                    ).edit(self._replyMessage.replace('____id____', str(newcomment.id)))
                else:
                    send_message()
            else:
                logger.info(str(author))
                send_message()
        except APIException.error_type("RATELIMIT"):
            logger.exception("RateLimitExceeded")
            # PM when I message too much
            send_message()
            time.sleep(10)
        except Forbidden:
            logger.exception("Forbidden")
            send_message()
        except APIException:  # Catch any less specific API errors
            logger.exception("APIException")
            # else:
            # print self._replyMessage

    def find_bot_child_comment(self):
        """
        Finds the clashcallerbot comment in the child
        """
        try:
            # Grabbing all child comments
            replies = reddit.submission(url=self.comment.permalink).comments[0].replies
            # Look for bot's reply
            commentfound = ""
            if replies:
                for comment in replies:
                    if str(comment.author) == "ClashCallerBot":
                        commentfound = comment
                self.comment_count(commentfound)
        except Exception:
            pass

    def comment_count(self, commentfound):
        """
        Posts edits the count if found
        """
        query = "SELECT count(permalink) FROM message_date WHERE permalink = %s"
        self._addToDB.cursor.execute(query, [self.comment.permalink])
        data = self._addToDB.cursor.fetchall()
        # Grabs the tuple within the tuple, a number/the count
        count = str(data[0][0])
        comment = reddit.comment(id=str(commentfound.id))
        body = comment.body
        # Adds the count to the post
        body = re.sub(r'(\d+ OTHERS |)CLICK(ED|) THIS LINK',
                      count + " OTHERS CLICKED THIS LINK",
                      body)
        comment.edit(body)


def grab_list_of_calls(username):
    """
    Grabs all the calls of the user
    """
    database = Connect()
    query = "SELECT permalink, message, new_date, id FROM message_date WHERE userid = %s ORDER BY new_date"
    database.cursor.execute(query, [username])
    data = database.cursor.fetchall()
    table = (
        "[**Click here to delete all your calls at once quickly.**]"
        "(http://www.reddit.com/message/compose/?to=ClashCallerBot&subject=Call&message=RemoveAll!)\n\n"
        "|Permalink|Message|Date|Remove|\n"
        "|-|-|-|:-:|")
    for row in data:
        date = str(row[2])
        table += (
            "\n|" + row[0] + "|" + row[1] + "|" +
            "[" + date + "](http://www.wolframalpha.com/input/?i=" + str(row[2]) + ")|"
            "[[X]](https://www.reddit.com/message/compose/?to=ClashCallerBot&subject=Remove&message=Remove!%20" + str(
                row[3]) + ")|"
        )
    if len(data) == 0:
        table = "Looks like you have no calls. Click the **[Custom]** button below to make one!"
    elif len(table) > 9000:
        table = "Sorry the comment was too long to display. Message /u/ClashCallerBotDbuggr " \
                "as this was his lazy error catching."
    table += Search.endMessage
    return table


def remove_reminder(username, idnum):
    """
    Deletes the reminder from the database
    """
    database = Connect()
    # only want userid to confirm if owner
    query = "SELECT userid FROM message_date WHERE id = %s"
    database.cursor.execute(query, [idnum])
    data = database.cursor.fetchall()
    deleteFlag = False
    for row in data:
        userid = str(row[0])
        # If the wrong ID number is given, item isn't deleted
        if userid == username:
            cmd = "DELETE FROM message_date WHERE id = %s"
            database.cursor.execute(cmd, [idnum])
            deleteFlag = True

    database.connection.commit()
    return deleteFlag


def remove_all(username):
    """
    Deletes all calls at once
    """
    database = Connect()
    query = "SELECT * FROM message_date where userid = %s"
    database.cursor.execute(query, [username])
    count = len(database.cursor.fetchall())
    cmd = "DELETE FROM message_date WHERE userid = %s"
    database.cursor.execute(cmd, [username])
    database.connection.commit()

    return count


def read_pm():
    try:
        for message in reddit.inbox.unread(mark_read=True, update_user=True):
            prawobject = isinstance(message, praw.models.Message)
            if (("clashcaller!" in message.body.lower() or "!clashcaller" in message.body.lower()) and prawobject):
                message.reply("Apologies, I cannot be invoked via PM. Please make a comment in the sub.")
                message.mark_as_read()
            elif (("delete!" in message.body.lower() or "!delete" in message.body.lower()) and prawobject):
                givenid = re.findall(r'delete!\s(.*?)$', message.body.lower())[0]
                givenid = 't1_' + givenid
                comment = reddit.comment(id=givenid)
                try:
                    #parentcomment = reddit.comment(id=comment.parent_id)
                    parentcomment = comment.parent()
                    if message.author.name == parentcomment.author.name:
                        comment.delete()
                except ValueError:
                    # comment wasn't inside the list
                    pass
                except AttributeError:
                    # comment might be deleted already
                    pass
                message.mark_as_read()
            elif (("mycalls!" in message.body.lower() or "!mycalls" in message.body.lower()) and prawobject):
                listOfCalls = grab_list_of_calls(message.author.name)
                message.reply(listOfCalls)
                message.mark_as_read()
            elif (("remove!" in message.body.lower() or "!remove" in message.body.lower()) and prawobject):
                givenid = re.findall(r'remove!\s(.*?)$', message.body.lower())[0]
                deletedFlag = remove_reminder(message.author.name, givenid)
                listOfCalls = grab_list_of_calls(message.author.name)
                # This means the user did own that reminder
                if deletedFlag:
                    message.reply("Call deleted. Your current Calls:\n\n" + listOfCalls)
                else:
                    message.reply(
                        "Try again with the current IDs that belong to you below. Your current Calls:\n\n" + listOfCalls)
                message.mark_as_read()
            elif (("removeall!" in message.body.lower() or "!removeall" in message.body.lower()) and prawobject):
                count = str(remove_all(message.author.name))
                listOfCalls = grab_list_of_calls(message.author.name)
                message.reply("I have deleted all **" + count + "** calls for you.\n\n" + listOfCalls)
                message.mark_as_read()
    except Exception:
        logger.exception(str(traceback.format_exc()))


def check_comment(comment):
    redditCall = Search(comment)
    if (("clashcaller!" in comment.body.lower() or
                 "!clashcaller" in comment.body.lower()) and
                redditCall.comment.id not in redditCall.commented and
                'ClashCallerBot' != str(comment.author) and
                START_TIME < redditCall.comment.created_utc):
        logger.info("in")
        t = Thread(target=redditCall.run())
        t.start()


# =============================================================================
# MAIN
# =============================================================================

def main():
    logger.info("start")

    while True:
        try:
            # grab the request
            request = requests.get('https://api.pushshift.io/reddit/search?q=%22ClashCaller%22&limit=100')
            json = request.json()
            comments = json["data"]
            read_pm()
            for rawcomment in comments:
                # object constructor requires empty attribute
                rawcomment['_replies'] = ''
                comment = praw.models.Comment(reddit, rawcomment)
                check_comment(comment)
            logger.info("----")
            time.sleep(30)
        except Exception:
            logger.exception(str(traceback.format_exc()))
            time.sleep(30)
        """
        Will add later if problem with api.pushshift
        hence why check_comment is a function
        try:
            for comment in praw.helpers.comment_stream(reddit, 'all', limit = 1, verbosity = 0):
                check_comment(comment)
        except Exception:
           logger.exception(str(traceback.format_exc()))
        """


# =============================================================================
# RUNNER
# =============================================================================

if __name__ == '__main__':
    main()
