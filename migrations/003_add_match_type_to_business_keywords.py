"""
Migration to add match_type field to business_keywords table.
This aligns the database schema with the technical specification.
"""

from yoyo import step

__depends__ = {"002_add_case_sensitive_to_business_and_keywords"}

steps = [
    step(
        "ALTER TABLE business_keywords ADD COLUMN match_type TEXT NOT NULL DEFAULT 'exact';",
        "ALTER TABLE business_keywords DROP COLUMN match_type;"
    ),
] 