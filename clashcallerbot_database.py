#! python3
# -*- coding: utf-8 -*-
"""Setup the MySQL-compatible database.

If run directly, this module will setup the clashcallerbot database with
tables and display their format and contents. Additionally,
this module provides a class with various methods for managing the
MySQL-compatible database:

* Create database and tables.
* View table data and properties.
* Grant user permissions (if logged into database as root).
* Add rows to tables.
* Delete tables and rows.
* Convert python datetime to MySQL datetime.
"""

import mysql.connector as mysql

import logging.config
import datetime

from logging_conf import LOGGING
from config import config

# Logger
logging.config.dictConfig(LOGGING)
logging.raiseExceptions = True  # Production mode if False (no console sys.stderr output)
logger = logging.getLogger('database')


class ClashCallerDatabase(object):
    """Implements a class for a ClashCaller Database.

    Attributes:
        config_file (configparser.ConfigParser()): A configparser object with database.ini file pre-read.
        root_user (bool): Specifies whether the database will be setup as root user.
        mysql_connection (mysql.connect()): A mysql.connector.connect() object.
        cursor (mysql.connect().cursor()): A mysql.connector.connect().cursor() object.
    """
    def __init__(self, config_file=None, root_user=None):
        if root_user is None:
            raise ValueError('root_user must be given.')
        if config_file is None:
            raise ValueError('A ConfigParser object must be given.')
        self._root_user = root_user
        if self._root_user:
            self._db_user = config_file['root']['user']
            self._db_pass = config_file['root']['password']

            self._bot_name = config_file['bot']['user']
            self._bot_passwd = config_file['bot']['password']
        else:
            self._db_user = config_file['bot']['user']
            self._db_pass = config_file['bot']['password']

        self._db_name = config_file['bot']['database']

        # Setup MySQL-compatible database
        try:
            self.mysql_connection = mysql.connect(user=self._db_user, password=self._db_pass, database=self._db_name)
            self.cursor = self.mysql_connection.cursor()
        except mysql.Error as err:
            logger.exception(f'mySQL connector and cursor: {err}')

    def __repr__(self):
        return f'ClashCallerDatabase(configparser.ConfigParser(\'database.ini\'), {self._root_user})'

    def __str__(self):
        return f'Logged into database: {self._db_name} as: {self._db_user}'

    def create_database(self) -> bool:
        """Create database

        Method creates database with database name.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self.cursor.execute(f'CREATE DATABASE {self._db_name};')
        except mysql.Error as err:
            logger.exception(f'create_database: {err}')
            return False
        return True

    def select_database(self) -> bool:
        """Select database for command execution.

        Method selects database within MySQL for command execution.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self.cursor.execute(f'USE {self._db_name};')
        except mysql.Error as err:
            logger.exception(f'select_database: {err}')
            return False
        return True

    def get_tables(self) -> list:
        """Return table list of database.

        Method returns a list with the names of the tables.

        Returns:
            table_names: List of table names.
        """
        table_names = []
        try:
            self.select_database()
            self.cursor.execute('SHOW TABLES;')
            tables = self.cursor.fetchall()

            for table in tables:
                table_names.append(str(table[0]))
        except mysql.Error as err:
            logger.exception(f'get_tables: {err}')
        return table_names

    def create_table(self, tbl_name: str, cols: str) -> bool:
        """Create table in database.

        Method creates table in database with given name and specifications.

        Args:
            tbl_name:   Name to give table.
            cols:       Columns to put in table.

        Example:
            ::
                tbl_name = 'table'
                cols = 'id INT UNSIGNED NOT NULL AUTO_INCREMENT, ' \
                       'permalink VARCHAR(100), message VARCHAR(100), new_date DATETIME, ' \
                       'userID VARCHAR(20), PRIMARY KEY(id)'

                create_table(tbl_name, cols)

        Returns:
            True if successful, False otherwise.
        """
        try:
            cmd = f'CREATE TABLE {tbl_name} ({cols})  ENGINE=InnoDB;'
            self.select_database()
            self.cursor.execute(cmd)

        except mysql.Error as err:
            logger.exception(f'create_table: {err}')
            return False
        return True

    def describe_table(self, tbl_name: str) -> list:
        """Gets description of table.

        Method returns a list describing the structure of the given table.

        Args:
            tbl_name:  Name of table to describe

        Returns:
            description: List with table description, empty list otherwise.
        """
        description = []
        try:
            self.cursor.execute(f'DESCRIBE {tbl_name};')
            description = self.cursor.fetchall()

        except mysql.Error as err:
            logger.exception(f'describe_table: {err}')
        return description

    def get_rows(self, tbl_name: str) -> tuple:
        """Fetch table rows.

        Method gets rows of given table by order of id in a tuple.

        Args:
            tbl_name:   Name of table to get rows from.
        Returns:
            rows:   Tuple containing each row's data, empty tuple otherwise.
        """
        rows = ()
        try:
            self.lock_read(tbl_name)
            self.cursor.execute(f'SELECT * FROM {tbl_name} GROUP BY id;')
            rows = tuple(self.cursor.fetchall())

        except mysql.Error as err:
            logger.exception(f'get_rows: {err}')
        return rows

    def grant_permissions(self) -> bool:
        """Grants bot user permissions to database.

        Method grants bot user permissions to database.

        Returns:
            True if successful, False otherwise.

        Notes:
            Only database root user can grant database permissions.
        """
        if not self._root_user:
            logger.error('Only root user can grant database permissions.')
            return False

        try:
            cmd = f'GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, ' \
                  f'CREATE TEMPORARY TABLES, LOCK TABLES ON {self._db_name}.* TO \'{self._bot_name}\'@localhost ' \
                  f'IDENTIFIED BY \'{self._bot_passwd}\';'
            self.cursor.execute(cmd)
        except mysql.Error as err:
            logger.exception(f'grant_permissions: {err}')
            return False
        return True

    def drop_table(self, tbl_name: str) -> bool:
        """Drop table from database.

        Function drops given table from given database.

        Args:
            tbl_name:   Table to drop.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self.select_database()
            self.lock_write(tbl_name)
            self.cursor.execute(f'DROP TABLE IF EXISTS {tbl_name};')

            if tbl_name in self.get_tables():
                return False
        except mysql.Error as err:
            logger.exception(f'drop_table: {err}')
            return False
        return True

    @staticmethod
    def convert_datetime(dt: datetime) -> datetime:
        """Converts python datetime to MySQL datetime.

        Method converts given python datetime object to MySQL datetime format.

        Args:
            dt: Datetime object in default format.

        Returns:
            Datetime object in MySQL format.
        """
        return dt.strftime('%Y-%m-%d %H:%M:%S')  # Convert to MySQL datetime

    def save_message(self, link: str, msg: str, exp: datetime, usr_name: str) -> bool:
        """Saves given comment data into message_data table.

        Method saves given inputs in message_date table as a row.

        Args:
            link:     Comment permalink.
            msg:      Comment message.
            exp:      Expiration datetime object.
            usr_name: Comment author username.

        Returns:
            True for success, false otherwise.
        """
        exp = self.convert_datetime(exp)
        try:
            self.lock_write('message_data')
            add_row = f'INSERT INTO message_data (permalink, message, new_date, userID) ' \
                      f'VALUES (\'{link}\', \'{msg}\', \'{exp}\', \'{usr_name}\');'
            self.cursor.execute(add_row)
            self.mysql_connection.commit()

        except mysql.Error as err:
            logger.exception(f'save_message: {err}')
            return False
        return True

    def delete_message(self, tid: str) -> bool:
        """Deletes message from message_data table.

        Method deletes given table id (row) from message_data table.

        Args:
            tid:    Table id from id column of message_data table.

        Returns:
            True for success, False otherwise.
        """
        try:
            self.lock_write('message_data')
            delete_row = f'DELETE FROM message_data WHERE id = \'{tid}\';'
            self.cursor.execute(delete_row)
            self.mysql_connection.commit()

        except mysql.Error as err:
            logger.exception(f'delete_message: {err}')
            return False
        return True

    def save_comment_id(self, cid: str) -> bool:
        """Saves comment id into comment_list table.

        Method saves given comment id into the comment_list table.

        Args:
            cid:    Comment id to save.

        Returns:
            True for success, false otherwise.
        """
        try:
            self.lock_write('comment_list')
            add_comment_id = f'INSERT INTO comment_list (comment_ids) VALUES (\'{cid}\');'

            self.cursor.execute(add_comment_id)
            self.mysql_connection.commit()

        except mysql.Error as err:
            logger.exception(f'save_comment_id: {err}')
            return False
        return True

    def find_comment_id(self, cid: str) -> bool:
        """Check comment_list table for comment id.

        Method checks comment_list table for given comment id.

        Args:
            cid:    Comment id to search for.

        Returns:
            True for success, false otherwise.
        """
        try:
            self.lock_read('comment_list')
            query = f'SELECT * FROM comment_list WHERE comment_ids=\'{cid}\' GROUP BY id;'
            self.cursor.execute(query)

            rows = self.cursor.fetchall()
            if not rows:
                return False

        except mysql.Error as err:
            logger.exception(f'find_comment_id: {err}')
            return False
        return True

    def get_messages(self, time_now: datetime.datetime) -> list:
        """Retrieves list of messages that have expired.

        Method returns list of messages whose expiration times are before current datetime.

        Args:
            time_now:   Current datetime.

        Returns:
            messages:   List containing results of query.
        """
        messages = []
        time_now = self.convert_datetime(time_now)
        try:
            self.lock_read('message_data')
            find_messages = f'SELECT * FROM message_data WHERE new_date < \'{time_now}\' GROUP BY id;'
            self.cursor.execute(find_messages)
            messages = self.cursor.fetchall()

        except mysql.Error as err:
            logger.exception(f'get_messages: {err}')
        return messages

    def lock_read(self, tbl_name: str) -> bool:
        """Locks table for reading.

        Method locks a given table for read access.

        Args:
            tbl_name:   Name of table to lock.

        Returns:
            True if successful, False otherwise.

        Notes:
            * Any previous locks are `implicitly released`_.
            * Read locks have lower priority than write locks.

        .. _implicitly released:
            https://dev.mysql.com/doc/refman/8.0/en/lock-tables.html
        """
        try:
            lock = f'LOCK TABLE {tbl_name} READ;'
            self.cursor.execute(lock)

        except mysql.Error as err:
            logger.exception(f'lock_read: {err}')
            return False
        return True

    def lock_write(self, tbl_name: str) -> bool:
        """Locks table for writing.

        Method locks a given table for write access.

        Args:
            tbl_name:   Name of table to lock.

        Returns:
            True if successful, False otherwise.

        Notes:
            * Any previous locks are `implicitly released`_.
            * Write locks have higher priority than read locks.

        .. _implicitly released:
            https://dev.mysql.com/doc/refman/8.0/en/lock-tables.html
        """
        try:
            lock = f'LOCK TABLE {tbl_name} WRITE;'
            self.cursor.execute(lock)

        except mysql.Error as err:
            logger.exception(f'lock_write: {err}')
            return False
        return True

    def close_connections(self) -> None:
        """Close database connections.

        Method closes database cursor and connection.

        Returns:
             None
        """
        self.cursor.close()
        self.mysql_connection.close()


def main():
    # Create the clashcaller database
    database = ClashCallerDatabase(config_file=config, root_user=False)

    # Select the clashcaller database
    database.select_database()

    # Show the tables
    print(database.get_tables())

    # Create message table
    # TODO: Store comment.id instead of permalink?
    col = 'id INT UNSIGNED NOT NULL AUTO_INCREMENT, ' \
          'permalink VARCHAR(100), message VARCHAR(100), new_date DATETIME, ' \
          'userID VARCHAR(20), PRIMARY KEY(id)'
    database.create_table('message_data', col)

    # Describe message table
    print(database.describe_table('message_data'))

    # Fetch rows from message_data as tuple of tuples
    print(database.get_rows('message_data'))

    # Create comment_list table
    # TODO: Add last run datetime to table for trimming
    col = 'id MEDIUMINT NOT NULL AUTO_INCREMENT, comment_ids VARCHAR(35), ' \
          'PRIMARY KEY(id)'
    database.create_table('comment_list', col)

    # Describe comment list table
    print(database.describe_table('comment_list'))

    # Fetch rows from comment_list as tuple of tuples
    print(database.get_rows('comment_list'))

    # Grant database bot permissions
    database.grant_permissions()

    # Close database connections
    database.close_connections()


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
