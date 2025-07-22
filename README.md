# OCR Invoice Parser

## Overview
The OCR Invoice Parser is a desktop application designed to extract structured data from PDF invoices using OCR (Optical Character Recognition) technology. It provides both a command-line interface (CLI) and a graphical user interface (GUI) built with PyQt6.

## Key Features
- OCR text extraction from PDF invoices using Tesseract
- Business name and keyword management with fuzzy matching
- Project and category management
- Configurable file naming templates
- Data persistence with SQLite
- Tabbed GUI for efficient workflow
- CLI for batch and automated processing

## Technology Stack
- Python 3.9+
- PyQt6
- SQLite
- Tesseract OCR
- pdf2image
- OpenCV

## Project Structure
```
src/ocr_receipt/
├── __init__.py
├── __main__.py
├── config.py
├── cli/
│   ├── __init__.py
│   ├── main.py
│   └── commands/
│       ├── __init__.py
│       ├── parse.py
│       ├── batch.py
│       └── test.py
├── gui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── single_pdf_tab.py
│   ├── business_keywords_tab.py
│   ├── projects_tab.py
│   ├── categories_tab.py
│   ├── file_naming_tab.py
│   ├── settings_tab.py
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── data_panel.py
│   │   ├── keywords_table.py
│   │   ├── projects_table.py
│   │   ├── categories_table.py
│   │   ├── editable_combo_box.py
│   │   └── pdf_preview.py
│   └── dialogs/
│       ├── __init__.py
│       ├── add_business_dialog.py
│       ├── edit_keyword_dialog.py
│       ├── add_project_dialog.py
│       ├── add_category_dialog.py
│       └── backup_restore_dialog.py
├── business/
│   ├── __init__.py
│   ├── database_manager.py
│   ├── business_mapping_manager.py
│   ├── project_manager.py
│   ├── category_manager.py
│   └── pdf_metadata_manager.py
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py
│   ├── invoice_parser.py
│   ├── credit_card_parser.py
│   └── date_extractor.py
├── core/
│   ├── __init__.py
│   ├── ocr_engine.py
│   ├── image_processor.py
│   ├── text_extractor.py
│   └── fuzzy_matcher.py
└── utils/
    ├── __init__.py
    ├── file_manager.py
    ├── filename_utils.py
    ├── amount_normalizer.py
    └── ocr_corrections.py
```

## Getting Started
1. Install Python 3.9+
2. Install Tesseract OCR
3. Clone this repository
4. Install Poetry: https://python-poetry.org/docs/#installation
5. Install dependencies: `poetry install`
6. Run tests: `poetry run pytest`
7. Start the application: `poetry run python -m ocr_receipt`

### Useful Commands
- Run the application:
  ```bash
  poetry run python -m ocr_receipt
  ```
- Run all tests:
  ```bash
  poetry run pytest
  ```

### Database Migrations
- Apply migrations to create/update database schema:
  ```bash
  poetry run yoyo apply --database sqlite:///your_database.db migrations/
  ```
- List applied migrations:
  ```bash
  poetry run yoyo list --database sqlite:///your_database.db
  ```
- Rollback migrations (if needed):
  ```bash
  poetry run yoyo rollback --database sqlite:///your_database.db
  ```

## License
MIT License 