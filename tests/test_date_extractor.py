import pytest
from ocr_receipt.parsers.date_extractor import DateExtractor

def test_extract_date_iso():
    extractor = DateExtractor()
    text = "Invoice date: 2024-06-01."
    assert extractor.extract_date(text) == "2024-06-01"

def test_extract_date_european():
    extractor = DateExtractor()
    text = "Date: 01/06/2024"
    assert extractor.extract_date(text) == "2024-06-01"

def test_extract_date_us():
    extractor = DateExtractor()
    text = "Date: 6/1/2024"
    # Should parse as 2024-01-06 or 2024-06-01 depending on pattern order; our pattern prefers DD/MM/YYYY
    assert extractor.extract_date(text) in ("2024-01-06", "2024-06-01")

def test_extract_date_long_month():
    extractor = DateExtractor()
    text = "Date: 1 June 2024"
    assert extractor.extract_date(text) == "2024-06-01"

def test_extract_date_month_first():
    extractor = DateExtractor()
    text = "Date: June 1, 2024"
    assert extractor.extract_date(text) == "2024-06-01"

def test_extract_all_dates():
    extractor = DateExtractor()
    text = "2024-06-01 and 01/06/2024 and January 15, 2024"
    dates = extractor.extract_all_dates(text)
    assert "2024-06-01" in dates
    assert "2024-01-15" in dates
    assert len(dates) >= 2

def test_validate_date():
    extractor = DateExtractor()
    assert extractor.validate_date("2024-06-01") is True
    assert extractor.validate_date("2024-13-01") is False
    assert extractor.validate_date("notadate") is False

def test_extract_date_none():
    extractor = DateExtractor()
    text = "No date here!"
    assert extractor.extract_date(text) is None 

def test_extract_date_french_long_month():
    extractor = DateExtractor()
    text = "Date: 1 juin 2024"
    assert extractor.extract_date(text) == "2024-06-01"

def test_extract_date_french_month_first():
    extractor = DateExtractor()
    text = "Date: juin 1, 2024"
    assert extractor.extract_date(text) == "2024-06-01"

def test_extract_date_french_accented():
    extractor = DateExtractor()
    text = "Date: 1 août 2024"
    assert extractor.extract_date(text) == "2024-08-01" 