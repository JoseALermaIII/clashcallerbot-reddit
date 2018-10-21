#! python3
# -*- coding: utf-8 -*-
"""Searches recent reddit comments for ClashCaller! string and saves to database.

This module uses the Python Reddit API Wrapper (PRAW) to search recent reddit comments
for the ClashCaller! string. If found, the username, comment time, message, and
expiration time (if any) are parsed. The default, or provided, expiration time is
applied, then all the comment data is saved to a MySQL-compatible database."""

import configparser  # TODO: Remove configparser
import logging.config

import praw
import mysql.connector as mysql
import re


def main():
    # Logger
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
    logging.raiseExceptions = True  # Production mode if False (no console sys.stderr output)
    logger = logging.getLogger('search')

    # Read database.ini file
    config = configparser.ConfigParser()
    config.read("database.ini")

    DB_USER = config.get("SQL", "user")
    DB_PASS = config.get("SQL", "passwd")
    DB_NAME = config.get("SQL", "name")

    # Setup MySQL-compatible database
    mysql_connection = mysql.connect(user=DB_USER, password=DB_PASS, database=DB_NAME)
    cursor = mysql_connection.cursor()

    # Generate reddit instance
    reddit = praw.Reddit('clashcaller')  # Section name in praw.ini
    subreddit = reddit.subreddit('ClashCallerBot')  # Limit scope for testing purposes

    # Search recent comments for ClashCaller! string
    clashcaller_re = re.compile(r'''
                                [!|\s]?             # prefix ! or space (optional)
                                [C|c]lash[C|c]aller # upper or lowercase ClashCaller
                                [!|\s]              # suffix ! or space (required)
                                ''', re.VERBOSE)
    for comment in subreddit.stream.comments():
        match = clashcaller_re.search(comment.body)
        if match and comment.author.name != 'ClashCallerBot':
            logger.info(f'In from {comment.author.name}: {comment.body}')
            # TODO: If found, parse username, comment date, message, permalink, and expiration time (if any)

            # Strip everything before and including ClashCaller! string
            comment.body = comment.body[match.end():].strip()
            logger.debug(f'Stripped comment body: {comment.body}')

            # Check for expiration time
            expiration_re = re.compile(r'''
                                       (\d){1,2}(\s)? # single or double digit (space after optional)
                                       (minute(s)?\s| # minute(s) (space after required)
                                       min\s|         # minute abbr. (space after required)
                                       hour(s)?\s|    # hour(s) (space after required)
                                       hr\s           # hour abbr. (space after required)
                                       )+''', re.VERBOSE)

    # TODO: Apply default, or provided expiration time to comment date

    # TODO: Save comment data to MySQL-compatible database

    # TODO: Compose message for comment and PM

    # TODO: If not already commented, comment and send PM


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
