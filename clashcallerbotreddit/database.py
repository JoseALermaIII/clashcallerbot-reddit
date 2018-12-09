#! python3
# -*- coding: utf-8 -*-
"""Setup the MySQL-compatible database.

If run directly, this module will setup the ClashCallerBot database with
tables and display their format and contents. Additionally,
this module provides a class with various methods for managing the
MySQL-compatible database:

* Create database and tables.
* View table data and properties.
* Lock tables for reading and writing.
* Grant user permissions (if logged into database as root).
* Add rows to tables.
* Delete tables and rows.
* Convert python datetime to MySQL datetime.
"""

import mysql.connector as mysql

import logging.config
import datetime

from clashcallerbotreddit import LOGGING, config

# Logger
logging.config.dictConfig(LOGGING)
logging.raiseExceptions = True  # Production mode if False (no console sys.stderr output)
logger = logging.getLogger('database')


class ClashCallerDatabase(object):
    """Implements a class for a ClashCaller Database.

    Acts as an object-relational mapper for mysql.connector specific to ClashCallerBot.

    Attributes:
        config_file (configparser.ConfigParser()): A configparser object with database.ini file pre-read.
        section (str): Section heading containing bot information. Defaults to 'bot'.
        root_user (bool): Specifies whether the database will be setup as root user.
        mysql_connection (mysql.connector.connect()): A mysql.connector.connect() object.
        cursor (mysql.connector.connect().cursor()): A mysql.connector.connect().cursor() object.
    """
    def __init__(self, config_file=None, section='bot', root_user=None):
        if root_user is None:
            raise ValueError('root_user must be given.')
        if config_file is None:
            raise ValueError('A ConfigParser object must be given.')
        self._root_user = root_user
        if self._root_user:
            self._db_user = config_file['root']['user']
            self._db_pass = config_file['root']['password']

            self._bot_name = config_file[section]['user']
            self._bot_passwd = config_file[section]['password']
        else:
            self._db_user = config_file[section]['user']
            self._db_pass = config_file[section]['password']

        self._db_name = config_file[section]['database']
        self._message_table = config_file[section]['message_table']

        # Initialize connections to None
        self.mysql_connection = None
        self.cursor = None

        # Then open connections
        self.open_connections()

    def __repr__(self):
        return f'ClashCallerDatabase(configparser.ConfigParser(\'database.ini\'), {self._root_user})'

    def __str__(self):
        return f'Logged into database: {self._db_name} as: {self._db_user}'

    def close_connections(self) -> None:
        """Close database connections.

        Method closes database cursor and connection.

        """
        try:
            self.cursor.close()
            self.mysql_connection.close()

        except mysql.Error as err:
            logger.exception(f'close_connections: {err}')

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

    def create_database(self) -> None:
        """Create database.

        Method creates database with database name.

        """
        try:
            self.cursor.execute(f'CREATE DATABASE {self._db_name};')
        except mysql.Error as err:
            logger.exception(f'create_database: {err}')

    def create_table(self, tbl_name: str, cols: str) -> None:
        """Create table in database.

        Method creates table in database with given name and specifications.

        Args:
            tbl_name:   Name to give table.
            cols:       Columns to put in table.

        Example:
            >>> from clashcallerbotreddit import config
            >>> from clashcallerbotreddit.database import ClashCallerDatabase
            >>> db = ClashCallerDatabase(config, root_user=False)
            >>> tbl_name = 'table'
            >>> cols = 'id INT UNSIGNED NOT NULL AUTO_INCREMENT, '
            ...        'permalink VARCHAR(100), message VARCHAR(100), new_date DATETIME, '
            ...        'userID VARCHAR(20), PRIMARY KEY(id)'
            ...
            >>> db.create_table(tbl_name, cols)

        """
        try:
            cmd = f'CREATE TABLE {tbl_name} ({cols})  ENGINE=InnoDB;'
            self.select_database()
            self.cursor.execute(cmd)

        except mysql.Error as err:
            logger.exception(f'create_table: {err}')

    def delete_message(self, tid: str) -> None:
        """Deletes message from message_data table.

        Method deletes given table id (row) from message_data table.

        Args:
            tid:    Table id from id column of message_data table.

        """
        try:
            self.lock_write(self._message_table)
            delete_row = f'DELETE FROM {self._message_table} WHERE id = \'{tid}\';'
            self.cursor.execute(delete_row)
            self.mysql_connection.commit()
            self.unlock_tables()

        except mysql.Error as err:
            logger.exception(f'delete_message: {err}')

    def describe_table(self, tbl_name: str) -> list:
        """Gets description of table.

        Method returns a list describing the structure of the given table.

        Args:
            tbl_name:  Name of table to describe

        Returns:
            List with table description, empty list otherwise.
        """
        description = []
        try:
            self.lock_read(tbl_name)
            self.cursor.execute(f'DESCRIBE {tbl_name};')
            description = self.cursor.fetchall()
            self.unlock_tables()

        except mysql.Error as err:
            logger.exception(f'describe_table: {err}')
        return description

    def drop_table(self, tbl_name: str) -> None:
        """Drop table from database.

        Function drops given table from given database.

        Args:
            tbl_name:   Table to drop.

        """
        try:
            self.select_database()
            tables = self.get_tables()
            if tbl_name not in tables:
                raise mysql.ProgrammingError('Table does not exist.')
            self.lock_write(tbl_name)
            self.cursor.execute(f'DROP TABLE IF EXISTS {tbl_name};')
            self.unlock_tables()

        except (mysql.Error, mysql.ProgrammingError) as err:
            logger.exception(f'drop_table: {err}')

    def get_messages(self, time_now: datetime.datetime) -> list:
        """Retrieves list of messages that have expired.

        Method returns list of messages whose expiration times are before current datetime.

        Args:
            time_now:   Current datetime.

        Returns:
            List containing results of query.
        """
        messages = []
        time_now = self.convert_datetime(time_now)
        try:
            self.lock_read(self._message_table)
            find_messages = f'SELECT * FROM {self._message_table} WHERE new_date < \'{time_now}\' GROUP BY id;'
            self.cursor.execute(find_messages)
            messages = self.cursor.fetchall()
            self.unlock_tables()

        except mysql.Error as err:
            logger.exception(f'get_messages: {err}')
        return messages

    def get_tables(self) -> list:
        """Return table list of database.

        Method returns a list with the names of the tables.

        Returns:
            List of table names.
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

    def get_rows(self, tbl_name: str) -> tuple:
        """Fetch table rows.

        Method gets rows of given table by order of id in a tuple.

        Args:
            tbl_name:   Name of table to get rows from.

        Returns:
            Tuple containing each row's data, empty tuple otherwise.
        """
        rows = ()
        try:
            self.lock_read(tbl_name)
            self.cursor.execute(f'SELECT * FROM {tbl_name} GROUP BY id;')
            rows = tuple(self.cursor.fetchall())
            self.unlock_tables()

        except mysql.Error as err:
            logger.exception(f'get_rows: {err}')
        return rows

    def grant_permissions(self) -> None:
        """Grants bot user permissions to database.

        Method grants bot user permissions to database.

        Notes:
            Only database root user can grant database permissions.
        """
        if not self._root_user:
            msg = 'Only root user can grant database permissions.'
            logger.error(msg)
            raise RuntimeError(msg)

        try:
            cmd = f'GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, ' \
                  f'CREATE TEMPORARY TABLES, LOCK TABLES ON {self._db_name}.* TO \'{self._bot_name}\'@localhost ' \
                  f'IDENTIFIED BY \'{self._bot_passwd}\';'
            self.cursor.execute(cmd)
        except (mysql.Error, RuntimeError) as err:
            logger.exception(f'grant_permissions: {err}')

    def lock_read(self, tbl_name: str) -> None:
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

    def lock_write(self, tbl_name: str) -> None:
        """Locks table for writing.

        Method locks a given table for write access.

        Args:
            tbl_name:   Name of table to lock.

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

    def open_connections(self) -> None:
        """Open database connections.

        Method makes database connection and cursor.

        """
        try:
            self.mysql_connection = mysql.connect(user=self._db_user, password=self._db_pass, database=self._db_name)
            self.cursor = self.mysql_connection.cursor()

        except mysql.Error as err:
            logger.exception(f'open_connections: {err}')

    def save_message(self, link: str, msg: str, exp: datetime, usr_name: str) -> None:
        """Saves given comment data into message_data table.

        Method saves given inputs in message_date table as a row.

        Args:
            link:     Comment permalink.
            msg:      Comment message.
            exp:      Expiration datetime object.
            usr_name: Comment author username.

        """
        exp = self.convert_datetime(exp)
        try:
            self.lock_write(self._message_table)
            add_row = f'INSERT INTO {self._message_table} (permalink, message, new_date, username) ' \
                      f'VALUES (\'{link}\', \'{msg}\', \'{exp}\', \'{usr_name}\');'
            self.cursor.execute(add_row)
            self.mysql_connection.commit()
            self.unlock_tables()

        except mysql.Error as err:
            logger.exception(f'save_message: {err}')

    def select_database(self) -> None:
        """Select database for command execution.

        Method selects database within MySQL for command execution.

        """
        try:
            self.cursor.execute(f'USE {self._db_name};')
        except mysql.Error as err:
            logger.exception(f'select_database: {err}')

    def unlock_tables(self) -> None:
        """Unlocks tables to allow access.

        Method unlocks tables to allow read/write access.

        """
        try:
            unlock = 'UNLOCK TABLES;'
            self.cursor.execute(unlock)

        except mysql.Error as err:
            logger.exception(f'unlock_tables: {err}')


def main():
    # Create the clashcaller database
    database = ClashCallerDatabase(config_file=config, root_user=False)

    # Select the clashcaller database
    database.select_database()

    # Show the tables
    tables = database.get_tables()
    print(tables)

    # Create message table, if it doesn't exist
    if database._message_table not in tables:
        col = 'id INT UNSIGNED NOT NULL AUTO_INCREMENT, ' \
              'permalink VARCHAR(100), message VARCHAR(100), new_date DATETIME, ' \
              'username VARCHAR(20), PRIMARY KEY(id)'
        database.create_table(database._message_table, col)
        tables = database.get_tables()

    # Describe message table
    print(database.describe_table(database._message_table))

    # Fetch rows from message_data as tuple of tuples
    print(database.get_rows(database._message_table))

    # Grant database bot permissions, if root
    if database._root_user:  # Direct access of protected member, but only to read. Should be okay...?
        database.grant_permissions()

    # Close database connections
    database.close_connections()


# If run directly, instead of imported as a module, run main():
if __name__ == '__main__':
    main()
