"""
Unit tests for InvoiceParser module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from decimal import InvalidOperation

from ocr_receipt.parsers.invoice_parser import InvoiceParser, InvoiceParserError


class TestInvoiceParser:
    """Test cases for InvoiceParser class."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        return {
            'ocr': {
                'tesseract_path': 'tesseract',
                'language': 'eng'
            },
            'parser': {
                'confidence_threshold': 0.5
            }
        }
    
    @pytest.fixture
    def parser(self, config):
        """Provide InvoiceParser instance."""
        return InvoiceParser(config)
    
    @pytest.fixture
    def sample_invoice_text(self):
        """Provide sample invoice text for testing."""
        return """
        ABC Company Inc.
        123 Business Street
        City, State 12345
        
        INVOICE
        
        Invoice Number: INV-2024-001
        Date: 2024-06-15
        
        Description: Consulting Services
        Amount: $1,250.00
        
        Total Amount Due: $1,250.00
        """
    
    def test_init(self, config):
        """Test InvoiceParser initialization."""
        parser = InvoiceParser(config)
        assert parser.config == config
        assert parser.date_extractor is not None
        assert len(parser.company_patterns) > 0
        assert len(parser.total_patterns) > 0
        assert len(parser.invoice_number_patterns) > 0
    
    def test_extract_company_with_label(self, parser):
        """Test company extraction with label."""
        text = "Company: ABC Corporation Inc."
        result = parser._extract_company(text)
        assert result == "ABC Corporation Inc."
    
    def test_extract_company_with_business_label(self, parser):
        """Test company extraction with business label."""
        text = "Business: XYZ Services LLC"
        result = parser._extract_company(text)
        assert result == "XYZ Services LLC"
    
    def test_extract_company_with_vendor_label(self, parser):
        """Test company extraction with vendor label."""
        text = "Vendor: Tech Solutions Corp."
        result = parser._extract_company(text)
        assert result == "Tech Solutions Corp."
    
    def test_extract_company_with_bill_from(self, parser):
        """Test company extraction with 'bill from' label."""
        text = "Bill from: Consulting Group Ltd."
        result = parser._extract_company(text)
        assert result == "Consulting Group Ltd."
    
    def test_extract_company_with_inc_suffix(self, parser):
        """Test company extraction with Inc. suffix."""
        text = "ABC Company Inc. provides services"
        result = parser._extract_company(text)
        assert result == "ABC Company Inc."
    
    def test_extract_company_with_llc_suffix(self, parser):
        """Test company extraction with LLC suffix."""
        text = "XYZ Services LLC"
        result = parser._extract_company(text)
        assert result == "XYZ Services LLC"
    
    def test_extract_company_fallback(self, parser):
        """Test company extraction fallback to line detection."""
        text = """
        ABC Company
        Invoice Number: INV-001
        Date: 2024-06-01
        """
        result = parser._extract_company(text)
        assert result == "ABC Company"
    
    def test_extract_company_no_match(self, parser):
        """Test company extraction when no match found."""
        text = "Invoice Number: INV-001\nDate: 2024-06-01\nTotal: $100"
        result = parser._extract_company(text)
        assert result is None
    
    def test_extract_total_with_label(self, parser):
        """Test total extraction with label."""
        text = "Total: $1,250.00"
        result = parser._extract_total(text)
        assert result == 1250.0
    
    def test_extract_total_with_amount_label(self, parser):
        """Test total extraction with amount label."""
        text = "Amount: $500.50"
        result = parser._extract_total(text)
        assert result == 500.5
    
    def test_extract_total_with_sum_label(self, parser):
        """Test total extraction with sum label."""
        text = "Sum: $750.25"
        result = parser._extract_total(text)
        assert result == 750.25
    
    def test_extract_total_with_balance_label(self, parser):
        """Test total extraction with balance label."""
        text = "Balance: $1,000.00"
        result = parser._extract_total(text)
        assert result == 1000.0
    
    def test_extract_total_with_due_label(self, parser):
        """Test total extraction with due label."""
        text = "Amount Due: $2,500.75"
        result = parser._extract_total(text)
        assert result == 2500.75
    
    def test_extract_total_with_grand_total(self, parser):
        """Test total extraction with grand total label."""
        text = "Grand Total: $3,750.00"
        result = parser._extract_total(text)
        assert result == 3750.0
    
    def test_extract_total_with_currency_symbol(self, parser):
        """Test total extraction with currency symbol."""
        text = "$1,250.00 Total"
        result = parser._extract_total(text)
        assert result == 1250.0
    
    def test_extract_total_with_currency_code(self, parser):
        """Test total extraction with currency code."""
        text = "$1,250.00 CAD"
        result = parser._extract_total(text)
        assert result == 1250.0
    
    def test_extract_total_fallback_currency_pattern(self, parser):
        """Test total extraction fallback to currency pattern."""
        text = "Services: $500.00\nTax: $50.00\nTotal: $550.00"
        result = parser._extract_total(text)
        assert result == 550.0  # Should return the largest amount
    
    def test_extract_total_with_commas(self, parser):
        """Test total extraction with comma-separated numbers."""
        text = "Total: $1,250,000.00"
        result = parser._extract_total(text)
        assert result == 1250000.0
    
    def test_extract_total_no_match(self, parser):
        """Test total extraction when no match found."""
        text = "Invoice Number: INV-001\nDate: 2024-06-01"
        result = parser._extract_total(text)
        assert result is None
    
    def test_extract_total_invalid_amount(self, parser):
        """Test total extraction with invalid amount."""
        text = "Total: $invalid"
        result = parser._extract_total(text)
        assert result is None
    
    def test_extract_date_iso_format(self, parser):
        """Test date extraction with ISO format."""
        text = "Date: 2024-06-15"
        result = parser._extract_date(text)
        assert result == "2024-06-15"
    
    def test_extract_date_us_format(self, parser):
        """Test date extraction with US format."""
        text = "Date: 06/15/2024"
        result = parser._extract_date(text)
        assert result == "2024-06-15"
    
    def test_extract_date_long_month(self, parser):
        """Test date extraction with long month name."""
        text = "Date: June 15, 2024"
        result = parser._extract_date(text)
        assert result == "2024-06-15"
    
    def test_extract_date_no_match(self, parser):
        """Test date extraction when no match found."""
        text = "Invoice Number: INV-001\nTotal: $100"
        result = parser._extract_date(text)
        assert result is None
    
    def test_extract_invoice_number_with_label(self, parser):
        """Test invoice number extraction with label."""
        text = "Invoice Number: INV-2024-001"
        result = parser._extract_invoice_number(text)
        assert result == "INV-2024-001"
    
    def test_extract_invoice_number_with_hash(self, parser):
        """Test invoice number extraction with hash symbol."""
        text = "Invoice #: INV-2024-001"
        result = parser._extract_invoice_number(text)
        assert result == "INV-2024-001"
    
    def test_extract_invoice_number_with_inv_label(self, parser):
        """Test invoice number extraction with inv label."""
        text = "Inv Number: INV-2024-001"
        result = parser._extract_invoice_number(text)
        assert result == "INV-2024-001"
    
    def test_extract_invoice_number_with_bill_label(self, parser):
        """Test invoice number extraction with bill label."""
        text = "Bill Number: BILL-2024-001"
        result = parser._extract_invoice_number(text)
        assert result == "BILL-2024-001"
    
    def test_extract_invoice_number_fallback_patterns(self, parser):
        """Test invoice number extraction with fallback patterns."""
        text = "INV-2024-001 invoice"
        result = parser._extract_invoice_number(text)
        assert result == "INV-2024-001"
    
    def test_extract_invoice_number_no_match(self, parser):
        """Test invoice number extraction when no match found."""
        text = "Date: 2024-06-01\nTotal: $100"
        result = parser._extract_invoice_number(text)
        assert result is None
    
    def test_calculate_confidence_all_fields_present(self, parser):
        """Test confidence calculation with all fields present."""
        result = {
            'company': 'ABC Company Inc.',
            'total': 1250.0,
            'date': '2024-06-15',
            'invoice_number': 'INV-2024-001'
        }
        confidence = parser._calculate_confidence(result)
        assert confidence > 0.8  # Should be high with all fields
    
    def test_calculate_confidence_partial_fields(self, parser):
        """Test confidence calculation with partial fields."""
        result = {
            'company': 'ABC Company',
            'total': 1250.0,
            'date': None,
            'invoice_number': None
        }
        confidence = parser._calculate_confidence(result)
        assert 0.4 <= confidence <= 0.6  # Should be moderate
    
    def test_calculate_confidence_no_fields(self, parser):
        """Test confidence calculation with no fields."""
        result = {
            'company': None,
            'total': None,
            'date': None,
            'invoice_number': None
        }
        confidence = parser._calculate_confidence(result)
        assert confidence == 0.0
    
    def test_calculate_confidence_bonus_points(self, parser):
        """Test confidence calculation with bonus points."""
        result = {
            'company': 'Very Long Company Name That Should Get Bonus',
            'total': 1250.0,
            'date': '2024-06-15',
            'invoice_number': 'INV-2024-001-LONG'
        }
        confidence = parser._calculate_confidence(result)
        assert confidence > 0.9  # Should be very high with bonuses
    
    def test_validate_result_valid(self, parser):
        """Test result validation with valid data."""
        result = {
            'company': 'ABC Company Inc.',
            'total': 1250.0,
            'date': '2024-06-15',
            'invoice_number': 'INV-2024-001'
        }
        is_valid = parser._validate_result(result)
        assert is_valid is True
    
    def test_validate_result_missing_fields(self, parser):
        """Test result validation with missing fields."""
        result = {
            'company': 'ABC Company Inc.',
            'total': 1250.0,
            'date': None,
            'invoice_number': 'INV-2024-001'
        }
        is_valid = parser._validate_result(result)
        assert is_valid is False
    
    def test_validate_result_invalid_total(self, parser):
        """Test result validation with invalid total."""
        result = {
            'company': 'ABC Company Inc.',
            'total': -100.0,
            'date': '2024-06-15',
            'invoice_number': 'INV-2024-001'
        }
        is_valid = parser._validate_result(result)
        assert is_valid is False
    
    def test_validate_result_invalid_date(self, parser):
        """Test result validation with invalid date."""
        result = {
            'company': 'ABC Company Inc.',
            'total': 1250.0,
            'date': 'invalid-date',
            'invoice_number': 'INV-2024-001'
        }
        is_valid = parser._validate_result(result)
        assert is_valid is False
    
    def test_validate_result_short_company(self, parser):
        """Test result validation with short company name."""
        result = {
            'company': 'A',
            'total': 1250.0,
            'date': '2024-06-15',
            'invoice_number': 'INV-2024-001'
        }
        is_valid = parser._validate_result(result)
        assert is_valid is False
    
    @patch('ocr_receipt.parsers.invoice_parser.InvoiceParser.extract_text')
    def test_parse_success(self, mock_extract_text, parser, sample_invoice_text):
        """Test successful parsing of invoice."""
        mock_extract_text.return_value = sample_invoice_text
        
        result = parser.parse(Path("test.pdf"))
        
        assert result['company'] == "ABC Company Inc."
        assert result['total'] == 1250.0
        assert result['date'] == "2024-06-15"
        assert result['invoice_number'] == "INV-2024-001"
        assert result['is_valid'] is True
        assert result['confidence'] > 0.8
        assert result['raw_text'] == sample_invoice_text
        assert result['pdf_path'] == "test.pdf"
    
    @patch('ocr_receipt.parsers.invoice_parser.InvoiceParser.extract_text')
    def test_parse_no_text_extracted(self, mock_extract_text, parser):
        """Test parsing when no text is extracted."""
        mock_extract_text.return_value = ""
        
        with pytest.raises(InvoiceParserError, match="No text extracted from PDF"):
            parser.parse(Path("test.pdf"))
    
    @patch('ocr_receipt.parsers.invoice_parser.InvoiceParser.extract_text')
    def test_parse_partial_extraction(self, mock_extract_text, parser):
        """Test parsing with partial extraction."""
        text = """
        ABC Company Inc.
        Invoice Number: INV-2024-001
        Date: 2024-06-15
        """
        mock_extract_text.return_value = text
        
        result = parser.parse(Path("test.pdf"))
        
        assert result['company'] == "ABC Company Inc."
        assert result['total'] is None
        assert result['date'] == "2024-06-15"
        assert result['invoice_number'] == "INV-2024-001"
        assert result['is_valid'] is False
        assert result['confidence'] < 0.8
    
    @patch('ocr_receipt.parsers.invoice_parser.InvoiceParser.extract_text')
    def test_parse_extraction_error(self, mock_extract_text, parser):
        """Test parsing when extraction raises an error."""
        mock_extract_text.side_effect = Exception("OCR failed")
        
        with pytest.raises(InvoiceParserError, match="Invoice parsing failed"):
            parser.parse(Path("test.pdf"))
    
    def test_extract_company_exception_handling(self, parser):
        """Test company extraction exception handling."""
        # This should not raise an exception
        result = parser._extract_company("")
        assert result is None
    
    def test_extract_total_exception_handling(self, parser):
        """Test total extraction exception handling."""
        # This should not raise an exception
        result = parser._extract_total("")
        assert result is None
    
    def test_extract_date_exception_handling(self, parser):
        """Test date extraction exception handling."""
        # This should not raise an exception
        result = parser._extract_date("")
        assert result is None
    
    def test_extract_invoice_number_exception_handling(self, parser):
        """Test invoice number extraction exception handling."""
        # This should not raise an exception
        result = parser._extract_invoice_number("")
        assert result is None
    
    def test_calculate_confidence_exception_handling(self, parser):
        """Test confidence calculation exception handling."""
        # This should not raise an exception and should return 0.0
        result = parser._calculate_confidence({})
        assert result == 0.0
    
    def test_validate_result_exception_handling(self, parser):
        """Test result validation exception handling."""
        # This should not raise an exception and should return False
        result = parser._validate_result({})
        assert result is False 