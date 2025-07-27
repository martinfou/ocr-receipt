"""
Unit tests for filename utilities module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from ocr_receipt.utils.filename_utils import (
    FilenameUtils, PDFMetadataHandler,
    generate_filename, clean_filename_part, validate_template, rename_file
)


class TestFilenameUtils:
    """Test cases for FilenameUtils class."""
    
    def test_generate_filename_basic(self):
        """Test basic filename generation."""
        template = "{project}_{date}_{company}"
        data = {
            'project': 'Q1_2024',
            'date': '2024-01-15',
            'company': 'Hydro Quebec'
        }
        
        result = FilenameUtils.generate_filename(template, data)
        expected = "Q1_2024_2024-01-15_Hydro_Quebec"
        assert result == expected
    
    def test_generate_filename_with_special_characters(self):
        """Test filename generation with special characters."""
        template = "{company}_{total}"
        data = {
            'company': 'Test & Company <LLC>',
            'total': '$1,234.56'
        }
        
        result = FilenameUtils.generate_filename(template, data)
        expected = "Test_&_Company_LLC_$1,234.56"
        assert result == expected
    
    def test_generate_filename_empty_template(self):
        """Test filename generation with empty template."""
        with pytest.raises(ValueError, match="Template cannot be empty"):
            FilenameUtils.generate_filename("", {})
    
    def test_generate_filename_invalid_template(self):
        """Test filename generation with invalid template."""
        template = "{invalid_variable}"
        data = {'project': 'test'}
        
        with pytest.raises(ValueError, match="Invalid template format"):
            FilenameUtils.generate_filename(template, data)
    
    def test_generate_filename_missing_variables(self):
        """Test filename generation with missing variables."""
        template = "{project}_{date}_{company}"
        data = {'project': 'test'}  # Missing date and company
        
        result = FilenameUtils.generate_filename(template, data)
        expected = "test"  # Empty placeholders are removed
        assert result == expected
    
    def test_clean_filename_part_basic(self):
        """Test basic filename part cleaning."""
        result = FilenameUtils.clean_filename_part("Test Company")
        assert result == "Test_Company"
    
    def test_clean_filename_part_special_characters(self):
        """Test cleaning special characters."""
        result = FilenameUtils.clean_filename_part("Test<Company>")
        assert result == "Test_Company"
    
    def test_clean_filename_part_multiple_spaces(self):
        """Test cleaning multiple spaces."""
        result = FilenameUtils.clean_filename_part("Test   Company")
        assert result == "Test_Company"
    
    def test_clean_filename_part_empty(self):
        """Test cleaning empty string."""
        result = FilenameUtils.clean_filename_part("")
        assert result == ""
    
    def test_clean_filename_part_none(self):
        """Test cleaning None value."""
        result = FilenameUtils.clean_filename_part(None)
        assert result == ""
    
    def test_validate_template_valid(self):
        """Test template validation with valid template."""
        template = "{project}_{date}_{company}"
        is_valid, errors = FilenameUtils.validate_template(template)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_template_empty(self):
        """Test template validation with empty template."""
        is_valid, errors = FilenameUtils.validate_template("")
        assert not is_valid
        assert "Template cannot be empty" in errors
    
    def test_validate_template_no_variables(self):
        """Test template validation with no variables."""
        is_valid, errors = FilenameUtils.validate_template("plain_text")
        assert not is_valid
        assert "Template must contain at least one variable" in errors
    
    def test_validate_template_invalid_variable(self):
        """Test template validation with invalid variable."""
        template = "{invalid_variable}"
        is_valid, errors = FilenameUtils.validate_template(template)
        assert not is_valid
        assert "Invalid variable 'invalid_variable'" in errors[0]
    
    def test_validate_template_unbalanced_braces(self):
        """Test template validation with unbalanced braces."""
        template = "{project}_{date"
        is_valid, errors = FilenameUtils.validate_template(template)
        assert not is_valid
        assert "Unbalanced braces in template" in errors
    
    def test_validate_template_empty_variable_name(self):
        """Test template validation with empty variable name."""
        template = "{project}_{}_{company}"
        is_valid, errors = FilenameUtils.validate_template(template)
        assert not is_valid
        assert "Empty variable names are not allowed" in errors
    
    def test_extract_variables_from_template(self):
        """Test extracting variables from template."""
        template = "{project}_{date}_{company}_{total}"
        variables = FilenameUtils.extract_variables_from_template(template)
        expected = ['project', 'date', 'company', 'total']
        assert variables == expected
    
    def test_extract_variables_from_template_with_spaces(self):
        """Test extracting variables with spaces."""
        template = "{ project }_{ date }"
        variables = FilenameUtils.extract_variables_from_template(template)
        expected = ['project', 'date']
        assert variables == expected
    
    def test_get_safe_filename_basic(self):
        """Test getting safe filename."""
        result = FilenameUtils.get_safe_filename("Test File.pdf")
        assert result == "Test_File.pdf"
    
    def test_get_safe_filename_with_path(self):
        """Test getting safe filename with path."""
        result = FilenameUtils.get_safe_filename("/path/to/Test File.pdf")
        assert result == "Test_File.pdf"
    
    def test_get_safe_filename_empty(self):
        """Test getting safe filename from empty string."""
        result = FilenameUtils.get_safe_filename("")
        assert result == "unnamed_file"
    
    def test_validate_filename_valid(self):
        """Test filename validation with valid filename."""
        is_valid, errors = FilenameUtils.validate_filename("valid_filename.pdf")
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_filename_empty(self):
        """Test filename validation with empty filename."""
        is_valid, errors = FilenameUtils.validate_filename("")
        assert not is_valid
        assert "Filename cannot be empty" in errors
    
    def test_validate_filename_invalid_characters(self):
        """Test filename validation with invalid characters."""
        is_valid, errors = FilenameUtils.validate_filename("test<file>.pdf")
        assert not is_valid
        assert "Filename contains invalid characters" in errors
    
    def test_validate_filename_reserved_name(self):
        """Test filename validation with reserved name."""
        is_valid, errors = FilenameUtils.validate_filename("CON.pdf")
        assert not is_valid
        assert "reserved system name" in errors[0]
    
    def test_validate_filename_too_long(self):
        """Test filename validation with too long filename."""
        long_filename = "a" * 256
        is_valid, errors = FilenameUtils.validate_filename(long_filename)
        assert not is_valid
        assert "Filename is too long (max 255 characters)" in errors
    
    def test_validate_filename_trailing_space(self):
        """Test filename validation with trailing space."""
        is_valid, errors = FilenameUtils.validate_filename("test.pdf ")
        assert not is_valid
        assert "Filename cannot end with space or dot" in errors
    
    def test_validate_filename_trailing_dot(self):
        """Test filename validation with trailing dot."""
        is_valid, errors = FilenameUtils.validate_filename("test.")
        assert not is_valid
        assert "Filename cannot end with space or dot" in errors


class TestFileRename:
    """Test cases for file rename functionality."""
    
    def test_rename_file_basic(self, tmp_path):
        """Test basic file rename."""
        # Create a test file
        test_file = tmp_path / "original.txt"
        test_file.write_text("test content")
        
        # Rename the file
        new_path = FilenameUtils.rename_file(str(test_file), "new_name")
        
        # Check that the file was renamed
        assert Path(new_path).exists()
        assert Path(new_path).read_text() == "test content"
        assert not test_file.exists()
    
    def test_rename_file_with_directory(self, tmp_path):
        """Test file rename with new directory."""
        # Create test directories
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()
        
        # Create a test file
        test_file = source_dir / "original.txt"
        test_file.write_text("test content")
        
        # Rename the file to new directory
        new_path = FilenameUtils.rename_file(str(test_file), "new_name", str(target_dir))
        
        # Check that the file was moved and renamed
        assert Path(new_path).exists()
        assert Path(new_path).read_text() == "test content"
        assert not test_file.exists()
        assert Path(new_path).parent == target_dir
    
    def test_rename_file_file_not_found(self):
        """Test file rename with non-existent file."""
        with pytest.raises(FileNotFoundError):
            FilenameUtils.rename_file("nonexistent.txt", "new_name")
    
    def test_rename_file_duplicate_name(self, tmp_path):
        """Test file rename with duplicate name."""
        # Create test files
        test_file1 = tmp_path / "original.txt"
        test_file1.write_text("content 1")
        
        test_file2 = tmp_path / "new_name.txt"
        test_file2.write_text("content 2")
        
        # Rename the first file
        new_path = FilenameUtils.rename_file(str(test_file1), "new_name")
        
        # Check that a number was added to avoid conflict
        assert Path(new_path).exists()
        assert Path(new_path).name == "new_name_1.txt"
        assert Path(new_path).read_text() == "content 1"
    
    def test_rename_file_preserves_extension(self, tmp_path):
        """Test that file rename preserves extension."""
        # Create a test file
        test_file = tmp_path / "original.pdf"
        test_file.write_text("test content")
        
        # Rename the file
        new_path = FilenameUtils.rename_file(str(test_file), "new_name")
        
        # Check that extension was preserved
        assert Path(new_path).suffix == ".pdf"
        assert Path(new_path).name == "new_name.pdf"


class TestPDFMetadataHandler:
    """Test cases for PDFMetadataHandler class."""
    
    @patch('ocr_receipt.utils.filename_utils.PDF_SUPPORT', True)
    @patch('ocr_receipt.utils.filename_utils.PdfReader')
    @patch('ocr_receipt.utils.filename_utils.PdfWriter')
    def test_save_variables_to_metadata(self, mock_pdf_writer, mock_pdf_reader, tmp_path):
        """Test saving variables to PDF metadata."""
        # Create a test PDF file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        
        # Mock PDF reader and writer
        mock_reader = MagicMock()
        mock_reader.metadata = {}
        mock_reader.pages = [MagicMock()]
        mock_pdf_reader.return_value = mock_reader
        
        mock_writer = MagicMock()
        mock_pdf_writer.return_value = mock_writer
        
        variables = {'project': 'test', 'company': 'Test Corp'}
        result = PDFMetadataHandler.save_variables_to_metadata(str(test_pdf), variables)
        
        assert result is True
        mock_writer.add_page.assert_called_once()
        mock_writer.add_metadata.assert_called_once()
    
    @patch('ocr_receipt.utils.filename_utils.PDF_SUPPORT', True)
    @patch('ocr_receipt.utils.filename_utils.PdfReader')
    def test_load_variables_from_metadata(self, mock_pdf_reader, tmp_path):
        """Test loading variables from PDF metadata."""
        # Create a test PDF file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        
        # Mock PDF reader with metadata
        mock_reader = MagicMock()
        variables = {'project': 'test', 'company': 'Test Corp'}
        mock_reader.metadata = {'/Keywords': '{"project": "test", "company": "Test Corp"}'}
        mock_pdf_reader.return_value = mock_reader
        
        result = PDFMetadataHandler.load_variables_from_metadata(str(test_pdf))
        assert result == variables
    
    @patch('ocr_receipt.utils.filename_utils.PDF_SUPPORT', True)
    @patch('ocr_receipt.utils.filename_utils.PdfReader')
    def test_load_variables_from_metadata_no_variables(self, mock_pdf_reader, tmp_path):
        """Test loading variables when none exist in metadata."""
        # Create a test PDF file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        
        # Mock PDF reader without metadata
        mock_reader = MagicMock()
        mock_reader.metadata = {}
        mock_pdf_reader.return_value = mock_reader
        
        result = PDFMetadataHandler.load_variables_from_metadata(str(test_pdf))
        assert result == {}
    
    @patch('ocr_receipt.utils.filename_utils.PDF_SUPPORT', True)
    @patch('ocr_receipt.utils.filename_utils.PdfReader')
    def test_has_variables_in_metadata_true(self, mock_pdf_reader, tmp_path):
        """Test checking for variables when they exist."""
        # Create a test PDF file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        
        # Mock PDF reader with metadata
        mock_reader = MagicMock()
        mock_reader.metadata = {'/Keywords': '{"test": "data"}'}
        mock_pdf_reader.return_value = mock_reader
        
        result = PDFMetadataHandler.has_variables_in_metadata(str(test_pdf))
        assert result is True
    
    @patch('ocr_receipt.utils.filename_utils.PDF_SUPPORT', True)
    @patch('ocr_receipt.utils.filename_utils.PdfReader')
    def test_has_variables_in_metadata_false(self, mock_pdf_reader, tmp_path):
        """Test checking for variables when they don't exist."""
        # Create a test PDF file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        
        # Mock PDF reader without metadata
        mock_reader = MagicMock()
        mock_reader.metadata = {}
        mock_pdf_reader.return_value = mock_reader
        
        result = PDFMetadataHandler.has_variables_in_metadata(str(test_pdf))
        assert result is False
    
    @patch('ocr_receipt.utils.filename_utils.PDF_SUPPORT', False)
    def test_save_variables_no_pdf_support(self, tmp_path):
        """Test saving variables when PyPDF2 is not available."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        
        variables = {'project': 'test'}
        result = PDFMetadataHandler.save_variables_to_metadata(str(test_pdf), variables)
        assert result is False
    
    @patch('ocr_receipt.utils.filename_utils.PDF_SUPPORT', False)
    def test_load_variables_no_pdf_support(self, tmp_path):
        """Test loading variables when PyPDF2 is not available."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        
        result = PDFMetadataHandler.load_variables_from_metadata(str(test_pdf))
        assert result == {}
    
    @patch('ocr_receipt.utils.filename_utils.PDF_SUPPORT', False)
    def test_has_variables_no_pdf_support(self, tmp_path):
        """Test checking for variables when PyPDF2 is not available."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        
        result = PDFMetadataHandler.has_variables_in_metadata(str(test_pdf))
        assert result is False
    
    def test_save_variables_file_not_found(self):
        """Test saving variables to non-existent file."""
        result = PDFMetadataHandler.save_variables_to_metadata("nonexistent.pdf", {})
        assert result is False
    
    def test_load_variables_file_not_found(self):
        """Test loading variables from non-existent file."""
        result = PDFMetadataHandler.load_variables_from_metadata("nonexistent.pdf")
        assert result == {}
    
    def test_has_variables_file_not_found(self):
        """Test checking for variables in non-existent file."""
        result = PDFMetadataHandler.has_variables_in_metadata("nonexistent.pdf")
        assert result is False


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    def test_generate_filename_convenience(self):
        """Test convenience function for filename generation."""
        template = "{project}_{company}"
        data = {'project': 'test', 'company': 'Test Corp'}
        
        result = generate_filename(template, data)
        expected = "test_Test_Corp"
        assert result == expected
    
    def test_clean_filename_part_convenience(self):
        """Test convenience function for cleaning filename parts."""
        result = clean_filename_part("Test Company")
        assert result == "Test_Company"
    
    def test_validate_template_convenience(self):
        """Test convenience function for template validation."""
        template = "{project}_{company}"
        is_valid, errors = validate_template(template)
        assert is_valid
        assert len(errors) == 0
    
    def test_rename_file_convenience(self, tmp_path):
        """Test convenience function for file rename."""
        # Create a test file
        test_file = tmp_path / "original.txt"
        test_file.write_text("test content")
        
        # Rename the file
        new_path = rename_file(str(test_file), "new_name")
        
        # Check that the file was renamed
        assert Path(new_path).exists()
        assert Path(new_path).read_text() == "test content"


class TestFilenameUtilsIntegration:
    """Integration tests for filename utilities."""
    
    def test_complete_workflow(self):
        """Test complete filename generation workflow."""
        # 1. Validate template
        template = "{project}_{date}_{company}_{total}"
        is_valid, errors = FilenameUtils.validate_template(template)
        assert is_valid
        
        # 2. Extract variables
        variables = FilenameUtils.extract_variables_from_template(template)
        expected_vars = ['project', 'date', 'company', 'total']
        assert variables == expected_vars
        
        # 3. Generate filename
        data = {
            'project': 'Q1_2024',
            'date': '2024-01-15',
            'company': 'Hydro Quebec Inc',
            'total': '$1,234.56'
        }
        
        filename = FilenameUtils.generate_filename(template, data)
        expected = "Q1_2024_2024-01-15_Hydro_Quebec_Inc_$1,234.56"
        assert filename == expected
        
        # 4. Validate generated filename
        is_valid, errors = FilenameUtils.validate_filename(f"{filename}.pdf")
        assert is_valid
    
    def test_edge_cases(self):
        """Test edge cases in filename generation."""
        # Test with very long company name
        template = "{company}"
        data = {'company': 'A' * 100}
        
        filename = FilenameUtils.generate_filename(template, data)
        assert len(filename) <= 255  # Should be within limits
        
        # Test with special characters
        template = "{company}_{total}"
        data = {
            'company': 'Test & Company <LLC> / "Special"',
            'total': '$1,234.56'
        }
        
        filename = FilenameUtils.generate_filename(template, data)
        # Should not contain invalid characters
        assert '<' not in filename
        assert '>' not in filename
        assert '"' not in filename
        assert '/' not in filename 