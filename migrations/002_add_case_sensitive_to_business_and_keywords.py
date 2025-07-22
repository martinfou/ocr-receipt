from yoyo import step

__depends__ = {"001_initial_schema"}

steps = [
    step(
        "ALTER TABLE businesses ADD COLUMN case_sensitive INTEGER NOT NULL DEFAULT 0;",
        "ALTER TABLE businesses DROP COLUMN case_sensitive;"
    ),
    step(
        "ALTER TABLE business_keywords ADD COLUMN case_sensitive INTEGER NOT NULL DEFAULT 0;",
        "ALTER TABLE business_keywords DROP COLUMN case_sensitive;"
    ),
] 