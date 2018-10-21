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

    # TODO: Search recent comments for ClashCaller! string

    # TODO: If found, parse username, comment date, message, and expiration time (if any)

    # TODO: Apply default, or provided expiration time to comment date

    # TODO: Save comment data to MySQL-compatible database


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
