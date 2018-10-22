#! python3
# -*- coding: utf-8 -*-
"""Setup the MySQL-compatible database.

This module provides various functions for managing the MySQL-compatible database:

* Create database and tables.
* View table data and properties.
* Grant user permissions (if logged into database as root).
* Add rows to tables.
* Delete tables.
"""

import mysql.connector as mysql

import configparser
import logging.config
import datetime

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


def main():
    local_cursor = mysql_connection.cursor()
    # Create the clashcaller database
    create_database(DB_NAME)

    # Select the clashcaller database
    local_cursor.execute(f'USE {DB_NAME};')

    # Show the tables
    print(get_tables(DB_NAME))

    # Create message table
    col = 'id INT UNSIGNED NOT NULL AUTO_INCREMENT, ' \
          'permalink VARCHAR(100), message VARCHAR(100), new_date DATETIME, ' \
          'userID VARCHAR(20), PRIMARY KEY(id)'
    create_table(DB_NAME, 'message_data', col)

    # Describe message table
    local_cursor.execute('DESCRIBE message_data;')
    print(local_cursor.fetchall())

    # Create comment_list table
    col = 'id MEDIUMINT NOT NULL AUTO_INCREMENT, comment_ids VARCHAR(35), ' \
          'PRIMARY KEY(id)'
    create_table(DB_NAME, 'comment_list', col)

    # Describe comment list table
    local_cursor.execute('DESCRIBE comment_list;')
    print(local_cursor.fetchall())

    # Fetch comment_ids column from comment_list
    local_cursor.execute('SELECT comment_ids FROM comment_list;')
    print(local_cursor.fetchall())

    # Grant database bot permissions
    if root_user:
        grant_permissions(DB_NAME, bot_name, bot_passwd)

    # Close database connections
    local_cursor.close()
    mysql_connection.close()


def create_database(db_name: str) -> bool:
    """Create database

    Function creates database with given database name.

    Args:
        db_name:    Name to give new database.

    Returns:
        True if successful, False otherwise.
    """
    try:
        cursor.execute(f'CREATE DATABASE {db_name};')
    except mysql.Error as err:
        logger.error(f'create_database: {err}')
        return False
    return True


def get_tables(db_name: str) -> list:
    """Return table list of given database.

    Function returns a list with the names of the tables.

    Args:
        db_name:    Database to get list of tables.

    Returns:
        table_names: List of table names.
    """
    table_names = []
    try:
        cursor.execute(f'USE {db_name}')
        cursor.execute('SHOW TABLES;')
        tables = cursor.fetchall()

        for table in tables:
            table_names.append(str(table[0]))
    except mysql.Error as err:
        logger.error(f'get_tables: {err}')
    return table_names


def create_table(db_name: str, tbl_name: str, cols: str) -> bool:
    """Create table in database.

    Function creates table in given database with name and specifications.

    Args:
        db_name:    Database to make table in.
        tbl_name:   Name to give table.
        cols:       Columns to put in table.

    Example:
        ::
            db_name = 'database'
            tbl_name = 'table'
            cols = 'id INT UNSIGNED NOT NULL AUTO_INCREMENT, ' \
                   'permalink VARCHAR(100), message VARCHAR(100), new_date DATETIME, ' \
                   'userID VARCHAR(20), PRIMARY KEY(id)'

            create_table(db_name, tbl_name, cols)

    Returns:
        True if successful, False otherwise.
    """
    try:
        cmd = f'CREATE TABLE {tbl_name} ({cols});'
        cursor.execute(f'USE {db_name}')
        cursor.execute(cmd)

    except mysql.Error as err:
        logger.error(f'create_table: {err}')
        return False
    return True


def grant_permissions(db_name: str, usr_name: str, usr_passwd: str) -> bool:
    """Grants user permissions to database.

    Function grants given user permissions to given database. However,
    only database root user can grant database permissions.

    Args:
        db_name:    Database to grant permissions to.
        usr_name:   User receiving permissions.
        usr_passwd: User's database authentication password.

    Example:
        ::
            db_name = 'database'
            usr_name = 'user'
            usr_passwd = 'not_my_password'

            create_table(db_name, usr_name, usr_passwd)

    Returns:
        True if successful, False otherwise.
    """
    try:
        cmd = f'GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, ' \
              f'CREATE TEMPORARY TABLES, LOCK TABLES ON {db_name}.* TO \'{usr_name}\'@localhost ' \
              f'IDENTIFIED BY \'{usr_passwd}\';'
        cursor.execute(cmd)
    except mysql.Error as err:
        logger.error(f'grant_permissions: {err}')
        return False
    return True


def drop_table(db_name: str, tbl_name: str) -> bool:
    """Drop table from database.

    Function drops given table from given database.

    Args:
        db_name:    Database to drop table from.
        tbl_name:   Table to drop.

    Returns:
        True if successful, False otherwise.
    """
    try:
        cursor.execute(f'USE {db_name};')
        cursor.execute(f'DROP TABLE IF EXISTS {tbl_name};')

        if tbl_name in get_tables(db_name):
            return False
    except mysql.Error as err:
        logger.error(f'drop_table: {err}')
        return False
    return True


def save_message(link: str, msg: str, exp: datetime, uid: str) -> bool:
    """Saves given comment data into message_data table.

    Function saves given inputs in message_date table as a row.

    Args:
        link:   Comment permalink.
        msg:    Comment message.
        exp:    Expiration datetime object.
        uid:    Comment author UserID.

    Returns:
        True for success, false otherwise.
    """
    try:
        add_row = f'INSERT INTO message_data (permalink, message, new_date, userID) ' \
                  f'VALUES ({link}, {msg}, {exp}, {uid})'
        cursor.execute(add_row)
        mysql_connection.commit()

    except mysql.Error as err:
        logger.error(f'save_message: {err}')
        return False
    return True


def save_comment_id(cid: str) -> bool:
    """Saves comment id into comment_list table.

    Function saves given comment id into the comment_list table.

    Args:
        cid:    Comment id to save.

    Returns:
        True for success, false otherwise.
    """
    try:
        add_comment_id = f'INSERT INTO comment_list (comment_ids) VALUES ({cid})'

        cursor.execute(add_comment_id)
        mysql_connection.commit()

    except mysql.Error as err:
        logger.error(f'save_comment_id: {err}')
        return False
    return True


def find_comment_id(cid: str) -> bool:
    """Check comment_list table for comment id.

    Function checks comment_list table for given comment id.

    Args:
        cid:    Comment id to search for.

    Returns:
        True for success, false otherwise.
    """
    try:
        query = 'SELECT comment_ids FROM comment_list;'
        cursor.execute(query)

        ids = cursor.fetchall()
        if cid not in ids:
            return False

    except mysql.Error as err:
        logger.error(f'find_comment_id: {err}')
        return False
    return True


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
