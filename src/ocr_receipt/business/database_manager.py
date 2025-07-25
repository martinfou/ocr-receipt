import sqlite3
from typing import Any, Optional, Sequence, Tuple, Union, Dict, List
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

    def add_keyword(self, business_id: int, keyword: str, is_case_sensitive: int = 0) -> bool:
        """
        Add a keyword for a business.
        :param business_id: ID of the business
        :param keyword: Keyword string
        :param is_case_sensitive: 0 (case-insensitive) or 1 (case-sensitive)
        :return: True if added, False if error
        """
        try:
            query = (
                "INSERT INTO business_keywords (business_id, keyword, is_case_sensitive) "
                "VALUES (?, ?, ?)"
            )
            self.execute_query(query, (business_id, keyword, is_case_sensitive))
            return True
        except Exception as e:
            logging.error(f"Failed to add keyword: {e}")
            return False

    def add_business(self, business_name: str, metadata: Optional[Dict] = None) -> int:
        """
        Add a new business to the database.
        :param business_name: Name of the business
        :param metadata: Optional metadata dictionary
        :return: Business ID if added successfully
        """
        try:
            query = "INSERT INTO businesses (name) VALUES (?)"
            cursor = self.execute_query(query, (business_name,))
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"Failed to add business: {e}")
            raise DatabaseError(f"Failed to add business: {e}")

    def get_all_businesses(self) -> List[Dict[str, Any]]:
        """
        Get all businesses from the database.
        :return: List of business dictionaries
        """
        try:
            query = "SELECT id, name FROM businesses"
            cursor = self.execute_query(query)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Failed to get businesses: {e}")
            return []

    def get_all_keywords(self):
        """
        Return all keywords with their associated business names and properties.
        """
        query = '''
            SELECT bk.keyword, bk.is_case_sensitive, bk.last_used, bk.usage_count, b.name as business_name
            FROM business_keywords bk
            JOIN businesses b ON bk.business_id = b.id
        '''
        cursor = self.execute_query(query)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()] 