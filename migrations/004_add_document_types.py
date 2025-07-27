"""
Add document types table migration
Creates document_types table for managing document type options
"""

from yoyo import step

__depends__ = {'001_initial_schema'}

steps = [
    step("""
        CREATE TABLE document_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            is_default BOOLEAN DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """, """
        DROP TABLE IF EXISTS document_types
    """),
    
    step("""
        INSERT INTO document_types (name, description, is_default, sort_order) VALUES 
        ('Invoice', 'Standard invoice documents', 1, 1),
        ('Credit Card', 'Credit card statements', 0, 2),
        ('Receipt', 'General receipts', 0, 3),
        ('Other', 'Other document types', 0, 4)
    """, """
        DELETE FROM document_types
    """),
    
    step("CREATE INDEX idx_document_types_name ON document_types(name)", 
         "DROP INDEX IF EXISTS idx_document_types_name"),
    step("CREATE INDEX idx_document_types_sort_order ON document_types(sort_order)", 
         "DROP INDEX IF EXISTS idx_document_types_sort_order")
] 