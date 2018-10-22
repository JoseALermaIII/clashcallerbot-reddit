#! python3
# -*- coding: utf-8 -*-
"""Setup the MySQL-compatible database.

This module provides various functions for managing the MySQL-compatible database.
The database and tables can be created. Table data and properties can also be viewed.
"""

import mysql.connector as mysql

import configparser
import logging.config


def main():
    # Logger
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
    logging.raiseExceptions = True  # Production mode if False (no console sys.stderr output)
    logger = logging.getLogger('database')

    # Read database.ini file
    config = configparser.ConfigParser()
    config.read("database.ini")

    root_user = False  # Change to True if first time setup
    if root_user:
        DB_USER = config.get('root', 'user')
        DB_PASS = config.get('root', 'password')

        bot_name = config.get('bot', 'user')
        bot_passwd = config.get('bot', 'password')
        DB_NAME = config.get('bot', 'database')
    else:
        DB_USER = config.get('bot', 'user')
        DB_PASS = config.get('bot', 'password')
        DB_NAME = config.get('bot', 'database')

    # Setup MySQL-compatible database
    mysql_connection = mysql.connect(user=DB_USER, password=DB_PASS, database=DB_NAME)
    cursor = mysql_connection.cursor()

    # Create the clashcaller database
    try:
        cursor.execute('CREATE DATABASE clashcaller;')
    except mysql.Error as err:
        logger.error(f'Create database err: {err}')

    # Select the clashcaller database
    cursor.execute('USE clashcaller;')

    # Show the tables
    cursor.execute('SHOW TABLES;')
    logger.info(f'Database tables: {cursor.fetchall()}')

    # Create message table
    try:
        cmd = 'CREATE TABLE message_date (id INT UNSIGNED NOT NULL AUTO_INCREMENT, ' \
              'permalink VARCHAR(100), message VARCHAR(100), new_date DATETIME, ' \
              'userID VARCHAR(20), PRIMARY KEY(id));'
        cursor.execute(cmd)

        cmd = 'ALTER TABLE message_date AUTO_INCREMENT=1;'
        cursor.execute(cmd)
    except mysql.Error as err:
        logger.error(f'Create message_table err: {err}')

    # Describe message table
    cursor.execute('DESCRIBE message_date;')
    print(cursor.fetchall())

    # Create comment list table
    try:
        cmd = 'CREATE TABLE comment_list (id MEDIUMINT NOT NULL, list VARCHAR(35), ' \
              'PRIMARY KEY(id));'
        cursor.execute(cmd)

        cmd = 'INSERT INTO comment_list VALUES (1, "\'0\'");'  # Initialize list column
        cursor.execute(cmd)
    except mysql.Error as err:
        logger.error(f'Create comment_list err: {err}')

    # Describe comment list table
    cursor.execute('DESCRIBE comment_list;')
    print(cursor.fetchall())

    # Fetch list column from comment_list
    cursor.execute('SELECT list FROM comment_list;')
    print(cursor.fetchall())

    # Grant database bot permissions
    if root_user:
        try:
            cmd = f'GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, ' \
                  f'CREATE TEMPORARY TABLES, LOCK TABLES ON {DB_NAME}.* TO \'{bot_name}\'@localhost ' \
                  f'IDENTIFIED BY \'{bot_passwd}\';'
            cursor.execute(cmd)
        except mysql.Error as err:
            logger.error(f'Grant bot permission err: {err}')


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
