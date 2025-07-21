import pytest
from ocr_receipt.business.database_manager import DatabaseManager, DatabaseError

def test_connect_and_close():
    db = DatabaseManager(':memory:')
    db.connect()
    assert db.connection is not None
    db.close()
    assert db.connection is None

def test_execute_query_create_insert_select():
    with DatabaseManager(':memory:') as db:
        db.execute_query('CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)')
        db.execute_query('INSERT INTO test (value) VALUES (?)', ("foo",))
        cursor = db.execute_query('SELECT value FROM test WHERE id = ?', (1,))
        result = cursor.fetchone()
        assert result[0] == "foo"

def test_execute_many():
    with DatabaseManager(':memory:') as db:
        db.execute_query('CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)')
        data = [("a",), ("b",), ("c",)]
        db.execute_many('INSERT INTO test (value) VALUES (?)', data)
        cursor = db.execute_query('SELECT COUNT(*) FROM test')
        count = cursor.fetchone()[0]
        assert count == 3

def test_error_handling():
    db = DatabaseManager(':memory:')
    db.connect()
    with pytest.raises(DatabaseError):
        db.execute_query('SELECT * FROM non_existent_table')
    db.close()

def test_context_manager():
    with DatabaseManager(':memory:') as db:
        db.execute_query('CREATE TABLE test (id INTEGER PRIMARY KEY)')
    # After context, connection should be closed
    assert db.connection is None 