# OCR Invoice Parser - Technical Specification

## Overview

The OCR Invoice Parser is a desktop application that extracts structured data from PDF invoices using OCR (Optical Character Recognition) technology. The application processes PDF files exclusively, converting PDF pages to images for OCR processing. The application provides both a command-line interface (CLI) and a graphical user interface (GUI) built with PyQt6.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    OCR Invoice Parser                       │
├─────────────────────────────────────────────────────────────┤
│  GUI Layer (PyQt6)                                          │
│  ├── Main Window                                            │
│  ├── Single PDF Processing Tab                             │
│  ├── Business Keywords Tab                                  │
│  ├── Projects Tab                                           │
│  ├── Categories Tab                                         │
│  ├── File Naming Tab                                        │
│  └── Settings Tab                                           │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                       │
│  ├── Business Mapping Manager                               │
│  ├── Project Manager                                        │
│  ├── Category Manager                                       │
│  ├── Database Manager                                       │
│  └── PDF Metadata Manager                                   │
├─────────────────────────────────────────────────────────────┤
│  Parser Layer                                               │
│  ├── Invoice Parser                                         │
│  ├── Credit Card Parser                                     │
│  ├── Date Extractor                                         │
│  └── Base Parser                                            │
├─────────────────────────────────────────────────────────────┤
│  Core Layer                                                 │
│  ├── OCR Engine                                             │
│  ├── Image Processor                                        │
│  ├── Text Extractor                                         │
│  └── Fuzzy Matcher                                          │
├─────────────────────────────────────────────────────────────┤
│  Data Layer (SQLite)                                        │
│  ├── Businesses                                             │
│  ├── Business Keywords                                      │
│  ├── Projects                                               │
│  ├── Categories                                             │
│  └── Invoice Metadata                                       │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Core Technologies
- **Python 3.8+**: Primary programming language
- **PyQt6**: GUI framework for desktop application
- **SQLite**: Embedded database for data persistence
- **Tesseract OCR**: OCR engine for PDF text extraction
- **pdf2image**: PDF to image conversion for OCR processing
- **OpenCV**: Image processing and manipulation for PDF pages

### Key Dependencies
- **pytesseract**: Python wrapper for Tesseract OCR
- **Pillow**: Image processing library
- **PyPDF2**: PDF manipulation
- **click**: CLI framework
- **pyyaml**: Configuration file parsing
- **pytest**: Testing framework
- **pytest-qt**: Qt testing support

## Database Schema

### Core Tables

#### 1. businesses
```sql
CREATE TABLE businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}'
);
```

#### 2. business_keywords
```sql
CREATE TABLE business_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    match_type TEXT NOT NULL DEFAULT 'exact',
    case_sensitive BOOLEAN DEFAULT FALSE,
    fuzzy_matching BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE,
    UNIQUE(business_id, keyword, match_type)
);
```

#### 3. projects
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. categories
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    category_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. invoice_metadata
```sql
CREATE TABLE invoice_metadata (
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
);
```

## Core Components

### 1. Configuration System

#### Configuration Manager
```python
class ConfigManager:
    """Manages application configuration from YAML files and environment variables."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = self._resolve_config_path(config_path)
        self.config = self._load_config()
    
    def get_config(self, reload: bool = False) -> Dict[str, Any]:
        """Get configuration dictionary."""
        pass
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        pass
    
    def _override_with_env(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Override config values with environment variables."""
        pass
```

#### Configuration Structure
```yaml
# default_config.yaml
ocr:
  language: "eng"
  tesseract_path: ""
  confidence_threshold: 0.6
  max_retries: 3

business_mapping:
  fuzzy_match_threshold: 0.3
  case_sensitive: false
  auto_backup: true
  max_backups: 10

file_naming:
  template: "{project}_{fileType}_{date}_{business}_{category}_{total}"
  date_format: "%Y-%m-%d"
  include_invoice_number: true

gui:
  window_size: [1600, 800]
  theme: "default"
  auto_save: true
  show_preview: true

database:
  path: "config/ocr_receipt.db"
  backup_interval: 24  # hours
  max_backup_age: 30   # days
```

### 2. Database Layer

#### Database Manager
```python
class DatabaseManager:
    """SQLite database manager for data persistence."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = self._resolve_db_path(db_path)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database tables."""
        pass
    
    # Business management
    def add_business(self, business_name: str, metadata: Optional[Dict] = None) -> int:
        """Add a new business."""
        pass
    
    def get_business(self, business_id: int) -> Optional[Dict]:
        """Get business by ID."""
        pass
    
    def get_all_businesses(self) -> List[Dict]:
        """Get all businesses."""
        pass
    
    # Keyword management
    def add_keyword(self, business_id: int, keyword: str, match_type: str = "exact") -> bool:
        """Add a keyword for a business."""
        pass
    
    def find_business_by_keyword(self, keyword: str) -> Optional[Dict]:
        """Find business by keyword."""
        pass
    
    # Project management
    def add_project(self, name: str, description: Optional[str] = None) -> int:
        """Add a new project."""
        pass
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects."""
        pass
    
    # Category management
    def add_category(self, name: str, description: Optional[str] = None) -> int:
        """Add a new category."""
        pass
    
    def get_all_categories(self) -> List[Dict]:
        """Get all categories."""
        pass
    
    # Metadata management
    def save_invoice_metadata(self, file_path: str, data: Dict) -> bool:
        """Save invoice metadata."""
        pass
    
    def get_invoice_metadata(self, file_path: str) -> Optional[Dict]:
        """Get invoice metadata."""
        pass
```

### 3. Business Logic Layer

#### Business Mapping Manager
```python
class BusinessMappingManager:
    """Manages business names and keywords for invoice matching."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_business(self, business_name: str) -> bool:
        """Add a new business."""
        pass
    
    def add_keyword(self, business_name: str, keyword: str, match_type: str = "exact") -> bool:
        """Add a keyword for a business."""
        pass
    
    def find_business_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find business match in text using exact, variant, and fuzzy matching."""
        pass
    
    def get_business_names(self) -> List[str]:
        """Get all business names."""
        pass
    
    def get_keywords(self) -> List[Dict[str, Any]]:
        """Get all keywords with business associations."""
        pass
```

#### Project Manager
```python
class ProjectManager:
    """Manages projects for invoice categorization."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_project(self, name: str, description: Optional[str] = None) -> int:
        """Add a new project."""
        pass
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects."""
        pass
    
    def update_project(self, project_id: int, name: str, description: Optional[str] = None) -> bool:
        """Update a project."""
        pass
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project."""
        pass
```

#### Category Manager
```python
class CategoryManager:
    """Manages categories for invoice classification."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_category(self, name: str, description: Optional[str] = None, category_code: Optional[str] = None) -> int:
        """Add a new category."""
        pass
    
    def get_all_categories(self) -> List[Dict]:
        """Get all categories."""
        pass
    
    def update_category(self, category_id: int, name: str, description: Optional[str] = None) -> bool:
        """Update a category."""
        pass
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category."""
        pass
```

### 4. Parser Layer

#### Base Parser
```python
class BaseParser:
    """Base class for all parsers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ocr_engine = OCREngine(config)
        self.text_extractor = TextExtractor(config)
        self.fuzzy_matcher = FuzzyMatcher()
    
    def parse(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse PDF and return structured data."""
        pass
    
    def extract_text(self, pdf_path: Union[str, Path]) -> str:
        """Extract text from PDF using OCR."""
        pass
    
    def validate_extraction_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and calculate confidence for extraction result."""
        pass
```

#### Invoice Parser
```python
class InvoiceParser(BaseParser):
    """Parser for extracting invoice data from PDFs."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.date_extractor = DateExtractor()
        self.business_mapping_manager = BusinessMappingManager(self.db_manager)
    
    def parse(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse invoice PDF and return structured data."""
        text = self.extract_text(pdf_path)
        
        result = {
            "company": self.extract_company(text),
            "total": self.extract_total(text),
            "date": self.extract_date(text),
            "invoice_number": self.extract_invoice_number(text),
            "raw_text": text,
            "parser_type": "invoice"
        }
        
        return self.validate_extraction_result(result)
    
    def extract_company(self, text: str) -> Optional[str]:
        """Extract company name using business mapping."""
        pass
    
    def extract_total(self, text: str) -> Optional[float]:
        """Extract total amount from text."""
        pass
    
    def extract_date(self, text: str) -> Optional[str]:
        """Extract invoice date from text."""
        pass
    
    def extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text."""
        pass
```

### 5. Core Layer

#### OCR Engine
```python
class OCREngine:
    """OCR engine using Tesseract for PDF processing."""
    
    def __init__(self, config: Dict[str, Any]):
        self.language = config.get("ocr", {}).get("language", "eng")
        self.tesseract_path = config.get("ocr", {}).get("tesseract_path", "")
        self.confidence_threshold = config.get("ocr", {}).get("confidence_threshold", 0.6)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from all pages in PDF using Tesseract OCR."""
        pass
    
    def extract_text_from_pdf_with_confidence(self, pdf_path: str) -> Tuple[str, float]:
        """Extract text from all pages in PDF with overall confidence score."""
        pass
    
    def extract_text_from_pdf_page(self, pdf_path: str, page_number: int) -> str:
        """Extract text from specific PDF page."""
        pass
    
    def extract_text_from_pdf_page_with_confidence(self, pdf_path: str, page_number: int) -> Tuple[str, float]:
        """Extract text from specific PDF page with confidence score."""
        pass
    
    def get_pdf_page_count(self, pdf_path: str) -> int:
        """Get the number of pages in a PDF."""
        pass
    
    def extract_text_from_all_pages(self, pdf_path: str) -> List[Tuple[int, str, float]]:
        """Extract text from all pages with page numbers and confidence scores."""
        pass
```

#### Image Processor
```python
class ImageProcessor:
    """Process PDF pages for better OCR results."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def convert_pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """Convert PDF pages to images for OCR processing."""
        pass
    
    def preprocess_pdf_page(self, image: np.ndarray) -> np.ndarray:
        """Preprocess PDF page image for better OCR."""
        pass
    
    def enhance_pdf_page(self, image: np.ndarray) -> np.ndarray:
        """Enhance PDF page image quality for OCR."""
        pass
    
    def get_pdf_page_count(self, pdf_path: str) -> int:
        """Get the number of pages in a PDF."""
        pass
```

#### Text Extractor
```python
class TextExtractor:
    """Extract and process text from PDF files."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ocr_engine = OCREngine(config)
        self.image_processor = ImageProcessor(config)
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from all pages in PDF file using OCR."""
        pass
    
    def extract_from_pdf_page(self, pdf_path: str, page_number: int) -> str:
        """Extract text from specific PDF page."""
        pass
    
    def extract_from_pdf_with_confidence(self, pdf_path: str) -> Tuple[str, float]:
        """Extract text from all pages in PDF with overall confidence score."""
        pass
    
    def extract_from_all_pages(self, pdf_path: str) -> List[Tuple[int, str, float]]:
        """Extract text from all pages with page numbers and confidence scores."""
        pass
```

#### Fuzzy Matcher
```python
class FuzzyMatcher:
    """Fuzzy string matching for business name matching."""
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
    
    def fuzzy_match(self, target: str, candidates: List[str]) -> Optional[str]:
        """Find best fuzzy match for target string."""
        pass
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        pass
```

### 6. GUI Layer

#### Main Window
```python
class OCRMainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager().get_config()
        self.db_manager = DatabaseManager()
        self._initialize_managers()
        self._setup_ui()
        self._setup_connections()
    
    def _initialize_managers(self):
        """Initialize business logic managers."""
        self.business_mapping_manager = BusinessMappingManager(self.db_manager)
        self.project_manager = ProjectManager(self.db_manager)
        self.category_manager = CategoryManager(self.db_manager)
    
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("OCR Invoice Parser")
        self._setup_page_navigation()
    
    def _setup_page_navigation(self):
        """Set up PDF page navigation controls."""
        # Page navigation toolbar
        self.page_toolbar = QToolBar("Page Navigation")
        self.addToolBar(self.page_toolbar)
        
        # Page navigation controls
        self.prev_page_btn = QPushButton("Previous Page")
        self.next_page_btn = QPushButton("Next Page")
        self.page_label = QLabel("Page 1 of 1")
        self.page_spinbox = QSpinBox()
        
        # Add controls to toolbar
        self.page_toolbar.addWidget(self.prev_page_btn)
        self.page_toolbar.addWidget(self.page_spinbox)
        self.page_toolbar.addWidget(self.page_label)
        self.page_toolbar.addWidget(self.next_page_btn)
        
        # Connect signals
        self.prev_page_btn.clicked.connect(self._previous_page)
        self.next_page_btn.clicked.connect(self._next_page)
        self.page_spinbox.valueChanged.connect(self._go_to_page)
    
    def _previous_page(self):
        """Navigate to previous page."""
        pass
    
    def _next_page(self):
        """Navigate to next page."""
        pass
    
    def _go_to_page(self, page_number: int):
        """Navigate to specific page."""
        pass
    
    def _update_page_navigation(self, current_page: int, total_pages: int):
        """Update page navigation controls."""
        pass
        self.setMinimumSize(1200, 600)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Create tabs
        self._create_single_pdf_tab()
        self._create_business_keywords_tab()
        self._create_projects_tab()
        self._create_categories_tab()
        self._create_file_naming_tab()
        self._create_settings_tab()
    
    def _create_single_pdf_tab(self):
        """Create single PDF processing tab."""
        pass
    
    def _create_business_keywords_tab(self):
        """Create business keywords management tab."""
        pass
    
    def _create_projects_tab(self):
        """Create projects management tab."""
        pass
    
    def _create_categories_tab(self):
        """Create categories management tab."""
        pass
```

#### Single PDF Tab
```python
class SinglePDFTab(QWidget):
    """Tab for processing single PDF files."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # File selection
        file_group = QGroupBox("PDF File")
        file_layout = QHBoxLayout(file_group)
        self.file_path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse...")
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_button)
        layout.addWidget(file_group)
        
        # Main content area (PDF viewer + data panel)
        content_layout = QHBoxLayout()
        
        # PDF viewer with page navigation
        pdf_group = QGroupBox("PDF Viewer")
        pdf_layout = QVBoxLayout(pdf_group)
        
        # Page navigation controls
        nav_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton("← Previous")
        self.next_page_btn = QPushButton("Next →")
        self.page_label = QLabel("Page 1 of 1")
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(1)
        
        nav_layout.addWidget(self.prev_page_btn)
        nav_layout.addWidget(self.page_spinbox)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.next_page_btn)
        nav_layout.addStretch()
        
        pdf_layout.addLayout(nav_layout)
        
        # PDF display area
        self.pdf_viewer = PDFViewer()
        pdf_layout.addWidget(self.pdf_viewer)
        
        content_layout.addWidget(pdf_group, 2)  # 2/3 of width
        
        # Data panel
        self.data_panel = DataPanel()
        content_layout.addWidget(self.data_panel, 1)  # 1/3 of width
        
        layout.addLayout(content_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.process_button = QPushButton("Process PDF")
        self.force_ocr_button = QPushButton("Force OCR")
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.force_ocr_button)
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """Set up signal connections."""
        self.browse_button.clicked.connect(self._on_browse_file)
        self.process_button.clicked.connect(self._on_process_pdf)
        self.force_ocr_button.clicked.connect(self._on_force_ocr)
        
        # Page navigation connections
        self.prev_page_btn.clicked.connect(self._previous_page)
        self.next_page_btn.clicked.connect(self._next_page)
        self.page_spinbox.valueChanged.connect(self._go_to_page)
    
    def _previous_page(self):
        """Navigate to previous page."""
        current_page = self.page_spinbox.value()
        if current_page > 1:
            self.page_spinbox.setValue(current_page - 1)
    
    def _next_page(self):
        """Navigate to next page."""
        current_page = self.page_spinbox.value()
        max_page = self.page_spinbox.maximum()
        if current_page < max_page:
            self.page_spinbox.setValue(current_page + 1)
    
    def _go_to_page(self, page_number: int):
        """Navigate to specific page."""
        self.pdf_viewer.display_page(page_number)
        self._update_page_navigation()
    
    def _update_page_navigation(self):
        """Update page navigation controls."""
        current_page = self.page_spinbox.value()
        total_pages = self.page_spinbox.maximum()
        self.page_label.setText(f"Page {current_page} of {total_pages}")
        
        # Enable/disable navigation buttons
        self.prev_page_btn.setEnabled(current_page > 1)
        self.next_page_btn.setEnabled(current_page < total_pages)
    
    def load_pdf(self, pdf_path: str):
        """Load PDF file and set up navigation."""
        self.pdf_viewer.load_pdf(pdf_path)
        total_pages = self.pdf_viewer.get_page_count()
        self.page_spinbox.setMaximum(total_pages)
        self.page_spinbox.setValue(1)
        self._update_page_navigation()
```

#### PDF Viewer
```python
class PDFViewer(QWidget):
    """Widget for displaying PDF pages with navigation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_path = None
        self.current_page = 1
        self.total_pages = 0
        self.page_images = {}  # Cache for page images
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # PDF display area
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setMinimumSize(400, 600)
        self.pdf_label.setStyleSheet("border: 1px solid #ccc; background: white;")
        layout.addWidget(self.pdf_label)
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        self.zoom_out_btn = QPushButton("Zoom Out")
        self.zoom_in_btn = QPushButton("Zoom In")
        self.zoom_fit_btn = QPushButton("Fit to View")
        self.zoom_label = QLabel("100%")
        
        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(self.zoom_in_btn)
        zoom_layout.addWidget(self.zoom_fit_btn)
        zoom_layout.addStretch()
        
        layout.addLayout(zoom_layout)
        
        # Connect zoom signals
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        self.zoom_fit_btn.clicked.connect(self._zoom_fit)
    
    def load_pdf(self, pdf_path: str):
        """Load PDF file and display first page."""
        self.pdf_path = pdf_path
        self.total_pages = self._get_page_count()
        self.current_page = 1
        self.page_images.clear()  # Clear cache
        self.display_page(1)
    
    def display_page(self, page_number: int):
        """Display specific page of the PDF."""
        if not self.pdf_path or page_number < 1 or page_number > self.total_pages:
            return
        
        self.current_page = page_number
        
        # Check cache first
        if page_number not in self.page_images:
            self.page_images[page_number] = self._load_page_image(page_number)
        
        # Display the page
        pixmap = self.page_images[page_number]
        self.pdf_label.setPixmap(pixmap)
    
    def get_page_count(self) -> int:
        """Get the total number of pages in the PDF."""
        return self.total_pages
    
    def _get_page_count(self) -> int:
        """Internal method to get page count."""
        # Implementation will use pdf2image or similar
        pass
    
    def _load_page_image(self, page_number: int) -> QPixmap:
        """Load page image and convert to QPixmap."""
        # Implementation will use pdf2image to convert PDF page to image
        pass
    
    def _zoom_out(self):
        """Zoom out the current page."""
        pass
    
    def _zoom_in(self):
        """Zoom in the current page."""
        pass
    
    def _zoom_fit(self):
        """Fit the current page to the view."""
        pass
```

#### Data Panel
```python
class DataPanel(QWidget):
    """Panel for displaying and editing extracted data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Data fields
        form_layout = QFormLayout()
        
        self.company_edit = QLineEdit()
        form_layout.addRow("Company:", self.company_edit)
        
        self.total_edit = QLineEdit()
        form_layout.addRow("Total:", self.total_edit)
        
        self.date_edit = QLineEdit()
        form_layout.addRow("Date:", self.date_edit)
        
        self.invoice_number_edit = QLineEdit()
        form_layout.addRow("Invoice Number:", self.invoice_number_edit)
        
        # Dropdowns
        self.project_combo = EditableComboBox()
        form_layout.addRow("Project:", self.project_combo)
        
        self.category_combo = EditableComboBox()
        form_layout.addRow("Category:", self.category_combo)
        
        layout.addLayout(form_layout)
        
        # File naming preview
        self.filename_preview = QLabel()
        layout.addWidget(self.filename_preview)
    
    def load_data(self, data: Dict[str, Any]):
        """Load extracted data into the panel."""
        self.company_edit.setText(data.get("company", ""))
        self.total_edit.setText(str(data.get("total", "")))
        self.date_edit.setText(data.get("date", ""))
        self.invoice_number_edit.setText(data.get("invoice_number", ""))
```

#### Business Keywords Tab
```python
class BusinessKeywordsTab(QWidget):
    """Tab for managing business keywords."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.business_mapping_manager = BusinessMappingManager(self.db_manager)
        self._setup_ui()
        self._setup_connections()
        self._load_keywords()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.add_button = QPushButton("Add Business")
        self.edit_button = QPushButton("Edit Keyword")
        self.delete_button = QPushButton("Delete Keyword")
        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Keywords table
        self.keywords_table = KeywordsTable()
        layout.addWidget(self.keywords_table)
        
        # Statistics
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)
    
    def _load_keywords(self):
        """Load keywords from database."""
        keywords = self.business_mapping_manager.get_keywords()
        self.keywords_table.load_keywords(keywords)
        self._update_statistics(keywords)
```

## File Structure

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

## Key Features

### 1. PDF Processing
- **OCR Text Extraction**: Extract text from PDF invoices using Tesseract
- **Multiple Parser Types**: Support for invoices and credit card statements
- **Confidence Scoring**: Calculate confidence for extracted data
- **Retry Logic**: Automatic retry for failed OCR attempts

### 2. Business Management
- **Business Names**: Store standardized business names
- **Keywords**: Associate keywords with business names for matching
- **Multiple Match Types**: Exact, variant, and fuzzy matching
- **Usage Tracking**: Track keyword usage and last used dates

### 3. Project & Category Management
- **Projects**: Organize invoices by projects
- **Categories**: Categorize invoices for reporting
- **Category Codes**: Support for custom category codes
- **Hierarchical Organization**: Nested project and category structures

### 4. File Naming
- **Template System**: Configurable file naming templates
- **Variable Substitution**: Use extracted data in filenames
- **Preview**: Real-time filename preview
- **Validation**: Ensure valid filenames

### 5. Data Persistence
- **SQLite Database**: Embedded database for data storage
- **Metadata Storage**: Store invoice metadata and processing results
- **Backup System**: Automatic backup and restore functionality
- **Migration Support**: Upgrade database schemas

### 6. User Interface
- **Tabbed Interface**: Organized workflow with multiple tabs
- **Real-time Updates**: Live updates as data changes
- **Search & Filter**: Find specific businesses, projects, or categories
- **Keyboard Shortcuts**: Efficient navigation and operations
- **Status Feedback**: Clear status messages and progress indicators

## Mockup Screens

### Main Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                    OCR Invoice Parser                       │
├─────────────────────────────────────────────────────────────┤
│  [🏠 Home] [📁 Single] [📂 Batch] [🔍 Search] [⚙️ Settings] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Quick Start   │  │ Recent Projects │  │ Statistics   │ │
│  │                 │  │                 │  │              │ │
│  │ • Single PDF    │  │ • Q1_2024       │  │ • Files      │ │
│  │ • Batch Folder  │  │ • Q4_2023       │  │ • Success    │ │
│  │ • Search PDFs   │  │ • Q3_2023       │  │ • Errors     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Recent Activity                                         │ │
│  │ • Processed invoice_001.pdf → ...                       │ │
│  │ • Batch completed: 47 files, 2 errors                   │ │
│  │ • Added alias: "Hydro Quebec" → "HYDRO-QUÉBEC"          │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

### Single PDF Mode

```
┌─────────────────────────────────────────────────────────────┐
│ Single PDF Processor                    [📁 Browse] [🔄]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐ │
│  │                 │  │ Project Settings                    │ │
│  │   PDF Preview   │  ├─────────────────────────────────────┤ │
│  │                 │  │ Project Name: [Q1_2024_____________]│ │
│  │                 │  │ Document Type: [Invoice ▼]         │ │
│  │                 │  │ Interactive Mode: [✓] Enabled      │ │
│  │                 │  │ Confidence Threshold: [80% ████████]│ │
│  │                 │  └─────────────────────────────────────┘ │
│  │                 │                                        │
│  │                 │  ┌─────────────────────────────────────┐ │
│  │                 │  │ Extracted Data                      │ │
│  │                 │  ├─────────────────────────────────────┤ │
│  │                 │  │ Company: [Hydro Quebec] [✓] [✏️]   │ │
│  │                 │  │ Date: [2024-01-15] [✓] [✏️]        │ │
│  │                 │  │ Total: [$1,234.56] [✓] [✏️]        │ │
│  │                 │  │ Invoice #: [INV-001] [⚠️] [✏️]     │ │
│  │                 │  └─────────────────────────────────────┘ │
│  └─────────────────┘                                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ File Naming Preview                                     │ │
│  │ Q1_2024_invoice_2024-01-15_hydro_quebec_$1234.56.pdf    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [🔄 Re-process] [💾 Save] [📁 Rename File] [📊 Export]      │
└─────────────────────────────────────────────────────────────┘
```

*Features: Drag-and-drop PDF, confidence indicators, inline edit, live filename preview, user confirmation for low-confidence fields.*

---

### Batch PDF Mode

```
┌─────────────────────────────────────────────────────────────┐
│ Batch PDF Processor                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Project Configuration                                   │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ Project Name: [Q1_2024_Invoices________________]        │ │
│  │ Folder: [📁 /Users/me/Documents/Invoices] [Browse]      │ │
│  │ Document Type: [Invoice ▼] Recursive: [✓] Subfolders    │ │
│  │ Interactive Mode: [✓] Only for low confidence           │ │
│  │ Confidence Threshold: [75% ████████]                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ File Discovery & Preview                                │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ Found 47 PDF files                                      │ │
│  │                                                         │ │
│  │ ┌─────────────────────────────────────────────────────┐ │ │
│  │ │ Filename          │ Size    │ Status  │ Preview     │ │ │
│  │ ├─────────────────────────────────────────────────────┤ │ │
│  │ │ invoice_001.pdf   │ 245 KB  │ [✓]     │ [👁️ View]   │ │ │
│  │ │ invoice_002.pdf   │ 189 KB  │ [✓]     │ [👁️ View]   │ │ │
│  │ │ invoice_003.pdf   │ 312 KB  │ [⚠️]     │ [👁️ View]   │ │ │
│  │ │ ...               │ ...     │ ...     │ ...         │ │ │
│  │ └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Processing Progress                                     │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ ████████████████████████████████████████████████████████  │ │
│  │ Processed: 23/47 files (48.9%)                          │ │
│  │ Success: 21 | Errors: 2 | Interactive: 0                │ │
│  │ Estimated time remaining: 2m 15s                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [▶️ Start Processing] [⏸️ Pause] [⏹️ Stop] [📊 Results]     │
└─────────────────────────────────────────────────────────────┘
```

*Features: Batch folder selection, progress bar, file table, interactive confirmation for low-confidence, batch renaming, export results.*

---

### PDF Search Tool

```
┌─────────────────────────────────────────────────────────────┐
│ PDF Content Search                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Search Configuration                                    │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ Search Folder: [📁 /Users/me/Documents] [Browse]        │ │
│  │ Search Term: [Hydro Quebec________________] [🔍 Search] │ │
│  │ Options: [✓] Case sensitive [✓] Fuzzy match [✓] Regex   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Search Results (23 matches found)                       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ ┌─────────────────────────────────────────────────────┐ │ │
│  │ │ Filename          │ Match Type │ Context            │ │ │
│  │ ├─────────────────────────────────────────────────────┤ │ │
│  │ │ invoice_001.pdf   │ Company    │ "Hydro Quebec Inc" │ │ │
│  │ │ invoice_002.pdf   │ Address    │ "Hydro Quebec St"  │ │ │
│  │ │ invoice_003.pdf   │ Total      │ "Hydro Quebec: $50"│ │ │
│  │ │ ...               │ ...        │ ...                │ │ │
│  │ └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [📁 Open Folder] [📊 Export Results] [🔍 New Search]       │
└─────────────────────────────────────────────────────────────┘
```

*Features: Folder picker, search bar with options, result table, export, open folder.*

---

### File Naming Template Builder

```
┌─────────────────────────────────────────────────────────────┐
│ File Naming Template Builder                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Template: [project_documentType_date_company_$total]       │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Template Components                                    │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [✓] Project Name    [project]                          │  │
│  │ [✓] Document Type   [documentType]                     │  │
│  │ [✓] Date            [date]                             │  │
│  │ [✓] Company         [company]                          │  │
│  │ [✓] Total Amount    [$total]                           │  │
│  │ [ ] Invoice Number  [invoiceNumber]                    │  │
│  │ [ ] Custom Text     [custom]                           │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Preview Examples                                       │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ Q1_2024_invoice_2024-01-15_hydro_quebec_$1234.56.pdf   │  │
│  │ Q1_2024_invoice_2024-01-16_royal_bank_$567.89.pdf      │  │
│  │ Q1_2024_invoice_2024-01-17_bell_canada_$234.12.pdf     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                             │
│  [💾 Save Template] [🔄 Reset] [❌ Cancel]                  │
└─────────────────────────────────────────────────────────────┘
```

*Features: Visual builder, live preview, validation, save/load templates, conflict handling in batch mode.*

---

### Interactive Confirmation Dialog (Low Confidence)

```
┌─────────────────────────────────────────────────────────────┐
│ Interactive Confirmation - Low Confidence Detection         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  File: invoice_003.pdf                                      │
│  Field: Company Name                                        │
│  Confidence: 65% (Low)                                      │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ PDF Context                                            │  │
│  │                                                        │  │
│  │ ...                                                    │  │
│  │ Invoice Date: 2024-01-17                               │  │
│  │ Company: Hydro Quebec Inc.                             │  │
│  │ Address: 123 Main Street                               │  │
│  │ ...                                                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Extracted Options                                       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ [✓] Hydro Quebec Inc. (65% confidence)                  │ │
│  │ [ ] Hydro Quebec (78% confidence)                       │ │
│  │ [ ] Hydro Quebec Inc (72% confidence)                   │ │
│  │ [ ] Enter manually: [________________]                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [✅ Confirm] [🔄 Re-scan] [⏭️ Skip] [❌ Cancel]            │
└─────────────────────────────────────────────────────────────┘
```

*Features: Shows context, confidence, options, manual entry, and action buttons. Batch mode only pauses for low-confidence fields.*

---

*Note: These are conceptual mockups. Actual UI may differ slightly based on implementation and platform conventions.*

## Configuration

### Environment Variables
- `OCR_RECEIPT_CONFIG_PATH`: Path to configuration file
- `OCR_RECEIPT_DB_PATH`: Path to SQLite database
- `OCR_RECEIPT_TESSERACT_PATH`: Path to Tesseract executable
- `OCR_RECEIPT_OCR_LANGUAGE`: OCR language (default: eng)

### Configuration File
The application uses YAML configuration files with the following structure:
- OCR settings (language, confidence threshold, retry count)
- Business mapping settings (fuzzy match threshold, case sensitivity)
- File naming templates and options
- GUI settings (window size, theme, auto-save)
- Database settings (backup intervals, cleanup policies)

## Testing Strategy

### Unit Tests
- **Parser Tests**: Test individual parser components
- **Business Logic Tests**: Test managers and data operations
- **Utility Tests**: Test helper functions and utilities
- **Database Tests**: Test database operations and migrations

### Integration Tests
- **End-to-End Tests**: Test complete PDF processing workflow
- **GUI Tests**: Test user interface interactions
- **Database Integration**: Test database operations with real data

### Test Framework
- **pytest**: Primary testing framework
- **pytest-qt**: Qt-specific testing support
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking and patching support

## Deployment

### Development Setup
1. Install Python 3.8+
2. Install Tesseract OCR
3. Clone repository
4. Install dependencies: `pip install -r requirements.txt`
5. Run tests: `pytest tests/`
6. Start application: `python -m ocr_receipt`

### Production Build
1. **PyInstaller**: Create standalone executables
2. **Folder Package**: Bundle with dependencies and Tesseract
3. **Installer**: Create Windows installer with NSIS
4. **CI/CD**: Automated builds with GitHub Actions

### Distribution
- **GitHub Releases**: Source code and binary releases
- **Installer Packages**: Windows .exe installer
- **Portable Packages**: Self-contained folder packages
- **Documentation**: User guides and API documentation

## Performance Considerations

### OCR Optimization
- **Image Preprocessing**: Enhance images for better OCR results
- **Confidence Filtering**: Filter low-confidence results
- **Parallel Processing**: Process multiple pages concurrently
- **Caching**: Cache OCR results for repeated processing

### Database Optimization
- **Indexing**: Proper database indexes for fast queries
- **Connection Pooling**: Efficient database connection management
- **Batch Operations**: Batch database operations for bulk data
- **Cleanup**: Regular cleanup of old data and backups

### Memory Management
- **Image Processing**: Efficient image handling and cleanup
- **Text Processing**: Stream processing for large text files
- **GUI Responsiveness**: Background processing to avoid UI blocking
- **Resource Cleanup**: Proper cleanup of temporary files and resources

## Security Considerations

### Data Protection
- **Local Storage**: All data stored locally on user's machine
- **No Network Access**: Application doesn't require internet access
- **File Permissions**: Respect file system permissions
- **Input Validation**: Validate all user inputs and file data

### Error Handling
- **Graceful Degradation**: Handle errors without crashing
- **User Feedback**: Clear error messages and recovery options
- **Logging**: Comprehensive logging for debugging
- **Data Recovery**: Backup and restore capabilities

## Future Enhancements

### Planned Features
- **Batch Processing**: Process multiple PDFs simultaneously
- **Advanced OCR**: Support for additional OCR engines
- **Cloud Integration**: Optional cloud storage and processing
- **Reporting**: Generate reports and analytics
- **API**: REST API for integration with other systems
- **Mobile Support**: Mobile application for invoice capture

### Technical Improvements
- **Performance**: Optimize OCR and processing speed
- **Accuracy**: Improve extraction accuracy with machine learning
- **Scalability**: Support for large document volumes
- **Integration**: Better integration with accounting software
- **Customization**: More flexible configuration and customization options

## Conclusion

This technical specification provides a comprehensive blueprint for re-coding the OCR Invoice Parser application. The architecture is designed to be modular, maintainable, and extensible, with clear separation of concerns between different layers. The use of SQLite for data persistence, PyQt6 for the GUI, and modern Python practices ensures a robust and user-friendly application.

The specification covers all major components including the database schema, business logic, parser architecture, GUI design, and deployment considerations. This document serves as a complete guide for implementing the application from scratch while maintaining the existing functionality and improving upon it. 