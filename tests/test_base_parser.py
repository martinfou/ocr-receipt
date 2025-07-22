import pytest
from src.ocr_receipt.parsers.base_parser import BaseParser

class DummyParser(BaseParser):
    def parse(self, pdf_path):
        return {"company": "TestCo", "total": 100.0, "date": "2024-06-01", "invoice_number": "INV-001"}

def test_parse_not_implemented():
    parser = BaseParser({})
    with pytest.raises(NotImplementedError):
        parser.parse("dummy.pdf")

def test_extract_text_calls_text_extractor(monkeypatch):
    called = {}
    class DummyTextExtractor:
        def extract_from_pdf(self, path):
            called["path"] = path
            return "some text"
    parser = BaseParser({})
    parser.text_extractor = DummyTextExtractor()
    result = parser.extract_text("file.pdf")
    assert result == "some text"
    assert called["path"] == "file.pdf"

def test_validate_extraction_result_and_confidence():
    parser = DummyParser({})
    # All fields present
    result = parser.parse("dummy.pdf")
    validated = parser.validate_extraction_result(result.copy())
    assert validated["is_valid"] is True
    assert validated["confidence"] == 1.0
    # Missing a required field
    incomplete = {"company": "TestCo", "total": 100.0, "date": "2024-06-01"}
    validated = parser.validate_extraction_result(incomplete)
    assert validated["is_valid"] is False
    assert validated["confidence"] == 0.5 