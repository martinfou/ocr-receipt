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

    def initialize_database(self) -> None:
        """
        Initialize the database with required tables.
        This method creates the basic schema if it doesn't exist.
        """
        try:
            # Create businesses table
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS businesses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            
            # Create business_keywords table
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS business_keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_id INTEGER NOT NULL,
                    keyword TEXT NOT NULL,
                    is_case_sensitive BOOLEAN DEFAULT 0,
                    last_used TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
                )
            ''')
            
            # Create projects table
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT
                )
            ''')
            
            # Create categories table
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    category_code TEXT
                )
            ''')
            
            # Create invoice_metadata table
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS invoice_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    business TEXT,
                    total REAL,
                    date TEXT,
                    invoice_number TEXT,
                    check_number TEXT,
                    raw_text TEXT,
                    parser_type TEXT,
                    confidence REAL,
                    is_valid BOOLEAN DEFAULT FALSE,
                    project_id INTEGER,
                    category_id INTEGER,
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

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

    def update_keyword(self, business_id: int, old_keyword: str, new_keyword: str, is_case_sensitive: int) -> bool:
        """
        Update an existing keyword for a business.
        :param business_id: ID of the business
        :param old_keyword: Original keyword to update
        :param new_keyword: New keyword text
        :param is_case_sensitive: 0 (case-insensitive) or 1 (case-sensitive)
        :return: True if updated, False if error
        """
        try:
            query = (
                "UPDATE business_keywords SET keyword = ?, is_case_sensitive = ? "
                "WHERE business_id = ? AND keyword = ?"
            )
            self.execute_query(query, (new_keyword, is_case_sensitive, business_id, old_keyword))
            return True
        except Exception as e:
            logging.error(f"Failed to update keyword: {e}")
            return False

    def delete_keyword(self, business_id: int, keyword: str) -> bool:
        """
        Delete a keyword for a business.
        :param business_id: ID of the business
        :param keyword: Keyword to delete
        :return: True if deleted, False if error
        """
        try:
            query = "DELETE FROM business_keywords WHERE business_id = ? AND keyword = ?"
            self.execute_query(query, (business_id, keyword))
            return True
        except Exception as e:
            logging.error(f"Failed to delete keyword: {e}")
            return False

    def get_keyword_id(self, business_id: int, keyword: str) -> Optional[int]:
        """
        Get the ID of a specific keyword.
        :param business_id: ID of the business
        :param keyword: Keyword text
        :return: Keyword ID if found, None otherwise
        """
        try:
            query = "SELECT id FROM business_keywords WHERE business_id = ? AND keyword = ?"
            cursor = self.execute_query(query, (business_id, keyword))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logging.error(f"Failed to get keyword ID: {e}")
            return None

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

    def get_keyword_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive keyword statistics for reporting.
        :return: Dictionary containing various statistics
        """
        try:
            stats = {}
            
            # Total counts
            cursor = self.execute_query("SELECT COUNT(*) FROM businesses")
            stats['total_businesses'] = cursor.fetchone()[0]
            
            cursor = self.execute_query("SELECT COUNT(*) FROM business_keywords")
            stats['total_keywords'] = cursor.fetchone()[0]
            
            # Case sensitivity breakdown
            cursor = self.execute_query("SELECT COUNT(*) FROM business_keywords WHERE is_case_sensitive = 1")
            stats['case_sensitive_keywords'] = cursor.fetchone()[0]
            
            cursor = self.execute_query("SELECT COUNT(*) FROM business_keywords WHERE is_case_sensitive = 0")
            stats['case_insensitive_keywords'] = cursor.fetchone()[0]
            
            # Usage statistics
            cursor = self.execute_query("SELECT SUM(usage_count) FROM business_keywords")
            total_usage = cursor.fetchone()[0]
            stats['total_usage'] = total_usage or 0
            
            cursor = self.execute_query("SELECT AVG(usage_count) FROM business_keywords")
            avg_usage = cursor.fetchone()[0]
            stats['average_usage'] = round(avg_usage or 0, 2)
            
            cursor = self.execute_query("SELECT MAX(usage_count) FROM business_keywords")
            max_usage = cursor.fetchone()[0]
            stats['max_usage'] = max_usage or 0
            
            # Most used keywords
            cursor = self.execute_query('''
                SELECT bk.keyword, bk.usage_count, b.name as business_name
                FROM business_keywords bk
                JOIN businesses b ON bk.business_id = b.id
                WHERE bk.usage_count > 0
                ORDER BY bk.usage_count DESC
                LIMIT 10
            ''')
            stats['most_used_keywords'] = [dict(zip(['keyword', 'usage_count', 'business_name'], row)) 
                                          for row in cursor.fetchall()]
            
            # Recently used keywords
            cursor = self.execute_query('''
                SELECT bk.keyword, bk.last_used, b.name as business_name
                FROM business_keywords bk
                JOIN businesses b ON bk.business_id = b.id
                WHERE bk.last_used IS NOT NULL
                ORDER BY bk.last_used DESC
                LIMIT 10
            ''')
            stats['recently_used_keywords'] = [dict(zip(['keyword', 'last_used', 'business_name'], row)) 
                                              for row in cursor.fetchall()]
            
            # Business with most keywords
            cursor = self.execute_query('''
                SELECT b.name, COUNT(bk.id) as keyword_count
                FROM businesses b
                LEFT JOIN business_keywords bk ON b.id = bk.business_id
                GROUP BY b.id, b.name
                ORDER BY keyword_count DESC
                LIMIT 10
            ''')
            stats['businesses_by_keyword_count'] = [dict(zip(['business_name', 'keyword_count'], row)) 
                                                   for row in cursor.fetchall()]
            
            # Unused keywords (never used)
            cursor = self.execute_query('''
                SELECT bk.keyword, b.name as business_name
                FROM business_keywords bk
                JOIN businesses b ON bk.business_id = b.id
                WHERE bk.usage_count = 0 OR bk.usage_count IS NULL
                ORDER BY b.name, bk.keyword
            ''')
            stats['unused_keywords'] = [dict(zip(['keyword', 'business_name'], row)) 
                                       for row in cursor.fetchall()]
            
            # Keywords by usage ranges
            cursor = self.execute_query('''
                SELECT 
                    CASE 
                        WHEN usage_count = 0 THEN 'Never Used'
                        WHEN usage_count BETWEEN 1 AND 5 THEN 'Low Usage (1-5)'
                        WHEN usage_count BETWEEN 6 AND 20 THEN 'Medium Usage (6-20)'
                        WHEN usage_count BETWEEN 21 AND 50 THEN 'High Usage (21-50)'
                        ELSE 'Very High Usage (50+)'
                    END as usage_range,
                    COUNT(*) as count
                FROM business_keywords
                GROUP BY usage_range
                ORDER BY 
                    CASE usage_range
                        WHEN 'Never Used' THEN 1
                        WHEN 'Low Usage (1-5)' THEN 2
                        WHEN 'Medium Usage (6-20)' THEN 3
                        WHEN 'High Usage (21-50)' THEN 4
                        WHEN 'Very High Usage (50+)' THEN 5
                    END
            ''')
            stats['keywords_by_usage_range'] = [dict(zip(['usage_range', 'count'], row)) 
                                               for row in cursor.fetchall()]
            
            return stats
            
        except Exception as e:
            logging.error(f"Failed to get keyword statistics: {e}")
            return {}

    def get_business_statistics(self) -> Dict[str, Any]:
        """
        Get business-specific statistics for reporting.
        :return: Dictionary containing business statistics
        """
        try:
            stats = {}
            
            # Business with highest total usage
            cursor = self.execute_query('''
                SELECT b.name, SUM(bk.usage_count) as total_usage
                FROM businesses b
                LEFT JOIN business_keywords bk ON b.id = bk.business_id
                GROUP BY b.id, b.name
                HAVING total_usage > 0
                ORDER BY total_usage DESC
                LIMIT 10
            ''')
            stats['businesses_by_total_usage'] = [dict(zip(['business_name', 'total_usage'], row)) 
                                                 for row in cursor.fetchall()]
            
            # Business with most recent activity
            cursor = self.execute_query('''
                SELECT b.name, MAX(bk.last_used) as last_used
                FROM businesses b
                LEFT JOIN business_keywords bk ON b.id = bk.business_id
                WHERE bk.last_used IS NOT NULL
                GROUP BY b.id, b.name
                ORDER BY last_used DESC
                LIMIT 10
            ''')
            stats['businesses_by_recent_activity'] = [dict(zip(['business_name', 'last_used'], row)) 
                                                     for row in cursor.fetchall()]
            
            # Business performance (average usage per keyword)
            cursor = self.execute_query('''
                SELECT b.name, 
                       COUNT(bk.id) as keyword_count,
                       AVG(bk.usage_count) as avg_usage_per_keyword
                FROM businesses b
                LEFT JOIN business_keywords bk ON b.id = bk.business_id
                GROUP BY b.id, b.name
                HAVING keyword_count > 0
                ORDER BY avg_usage_per_keyword DESC
                LIMIT 10
            ''')
            stats['businesses_by_avg_usage'] = [dict(zip(['business_name', 'keyword_count', 'avg_usage_per_keyword'], row)) 
                                               for row in cursor.fetchall()]
            
            return stats
            
        except Exception as e:
            logging.error(f"Failed to get business statistics: {e}")
            return {}

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance and efficiency metrics for reporting.
        :return: Dictionary containing performance metrics
        """
        try:
            metrics = {}
            
            # Keyword efficiency (usage vs. total keywords)
            cursor = self.execute_query("SELECT COUNT(*) FROM business_keywords WHERE usage_count > 0")
            used_keywords = cursor.fetchone()[0]
            
            cursor = self.execute_query("SELECT COUNT(*) FROM business_keywords")
            total_keywords = cursor.fetchone()[0]
            
            if total_keywords > 0:
                metrics['keyword_efficiency'] = round((used_keywords / total_keywords) * 100, 2)
            else:
                metrics['keyword_efficiency'] = 0
            
            # Average keywords per business
            cursor = self.execute_query("SELECT COUNT(*) FROM businesses")
            total_businesses = cursor.fetchone()[0]
            
            if total_businesses > 0:
                metrics['avg_keywords_per_business'] = round(total_keywords / total_businesses, 2)
            else:
                metrics['avg_keywords_per_business'] = 0
            
            # Most efficient keywords (high usage relative to age)
            cursor = self.execute_query('''
                SELECT bk.keyword, bk.usage_count, b.name as business_name
                FROM business_keywords bk
                JOIN businesses b ON bk.business_id = b.id
                WHERE bk.usage_count > 0
                ORDER BY bk.usage_count DESC
                LIMIT 5
            ''')
            metrics['most_efficient_keywords'] = [dict(zip(['keyword', 'usage_count', 'business_name'], row)) 
                                                for row in cursor.fetchall()]
            
            return metrics
            
        except Exception as e:
            logging.error(f"Failed to get performance metrics: {e}")
            return {} 