-- Initial schema migration for OCR Invoice Parser
-- Creates all required tables with proper relationships and indexes

-- Businesses table
CREATE TABLE businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Business keywords table (for fuzzy matching)
CREATE TABLE business_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    is_case_sensitive BOOLEAN DEFAULT 0,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    UNIQUE(business_id, keyword)
);

-- Projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table (with category code support)
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_code TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoice metadata table
CREATE TABLE invoice_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    business_id INTEGER,
    project_id INTEGER,
    category_id INTEGER,
    invoice_number TEXT,
    invoice_date DATE,
    total_amount DECIMAL(10,2),
    ocr_confidence DECIMAL(3,2),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Create indexes for frequently queried columns
CREATE INDEX idx_business_keywords_keyword ON business_keywords(keyword);
CREATE INDEX idx_business_keywords_business_id ON business_keywords(business_id);
CREATE INDEX idx_invoice_metadata_business_id ON invoice_metadata(business_id);
CREATE INDEX idx_invoice_metadata_project_id ON invoice_metadata(project_id);
CREATE INDEX idx_invoice_metadata_category_id ON invoice_metadata(category_id);
CREATE INDEX idx_invoice_metadata_invoice_date ON invoice_metadata(invoice_date);
CREATE INDEX idx_invoice_metadata_filename ON invoice_metadata(filename); 