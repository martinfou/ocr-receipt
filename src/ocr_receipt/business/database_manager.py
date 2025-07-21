import sqlite3
from typing import Any, Optional, Sequence, Tuple, Union
import logging

class DatabaseError(Exception):
    """Custom exception for database errors."""
    pass

class DatabaseManager:
    """
    Manages SQLite database connections and query execution.
    Usage:
        with DatabaseManager('mydb.sqlite') as db:
            db.execute_query('SELECT * FROM mytable')
    """
    def __init__(self, db_path: str) -> None:
        """
        Initialize the DatabaseManager.
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None

    def __enter__(self) -> 'DatabaseManager':
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def connect(self) -> None:
        """
        Open a connection to the SQLite database.
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            raise DatabaseError(f"Connection failed: {e}")

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: Optional[Union[Sequence[Any], dict]] = None) -> sqlite3.Cursor:
        """
        Execute a parameterized query and return the cursor.
        :param query: SQL query string.
        :param params: Query parameters (tuple/list or dict).
        :return: sqlite3.Cursor
        """
        if self.connection is None:
            self.connect()
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            logging.error(f"Database query failed: {e}\nQuery: {query}\nParams: {params}")
            raise DatabaseError(f"Query failed: {e}")

    def execute_many(self, query: str, seq_of_params: Sequence[Sequence[Any]]) -> None:
        """
        Execute a parameterized query against a sequence of parameter sets.
        :param query: SQL query string.
        :param seq_of_params: Sequence of parameter tuples/lists.
        """
        if self.connection is None:
            self.connect()
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, seq_of_params)
            self.connection.commit()
        except sqlite3.Error as e:
            logging.error(f"Database batch query failed: {e}\nQuery: {query}")
            raise DatabaseError(f"Batch query failed: {e}") 