"""
Filename utilities for OCR Receipt Parser.

This module provides centralized functionality for:
- Filename generation from templates
- Variable substitution
- Filename validation and cleaning
- File rename operations
- PDF metadata handling for hidden variables
"""

import re
import os
import shutil
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

try:
    from pypdf import PdfReader, PdfWriter
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logging.warning("pypdf not available. PDF metadata functionality will be disabled.")

logger = logging.getLogger(__name__)


class FilenameUtils:
    """Utility class for filename operations."""
    
    # Valid template variables
    VALID_VARIABLES = {
        'project', 'documentType', 'date', 'company', 'total', 
        'invoiceNumber', 'checkNumber', 'category', 'categoryCode'
    }
    
    # Invalid filename characters (Windows and Unix)
    INVALID_CHARS = r'[<>:"/\\|?*\x00-\x1f]'
    
    def __init__(self):
        """Initialize the filename utilities."""
        pass
    
    @staticmethod
    def generate_filename(template: str, data: Dict[str, str]) -> str:
        """
        Generate filename from template and data.
        
        Args:
            template: Template string with variables in {variable} format
            data: Dictionary of variable names and values
            
        Returns:
            Generated filename string
            
        Raises:
            ValueError: If template is invalid or data is missing required variables
        """
        try:
            if not template:
                raise ValueError("Template cannot be empty")
            
            # Validate template format
            if not FilenameUtils._validate_template_format(template):
                raise ValueError("Invalid template format")
            
            # Replace variables in template
            result = template
            for var_name, value in data.items():
                placeholder = f"{{{var_name}}}"
                if placeholder in result:
                    # Clean the value for filename use
                    clean_value = FilenameUtils.clean_filename_part(value)
                    result = result.replace(placeholder, clean_value)
            
            # Clean up any remaining placeholders
            result = re.sub(r'\{[^}]+\}', '', result)
            
            # Clean up separators - preserve hyphens, only normalize underscores
            result = re.sub(r'_+', '_', result)  # Multiple underscores to single underscore
            result = result.strip('_')  # Only strip underscores, preserve hyphens
            
            # Final validation
            if not result:
                raise ValueError("Generated filename is empty")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate filename: {e}")
            raise
    
    @staticmethod
    def clean_filename_part(value: str) -> str:
        """
        Clean a value for use in filename.
        
        Args:
            value: Raw value to clean
            
        Returns:
            Cleaned value safe for filename use
        """
        if not value:
            return ""
        
        # Replace invalid filename characters
        cleaned = re.sub(FilenameUtils.INVALID_CHARS, '_', value)
        
        # Replace spaces with underscores
        cleaned = re.sub(r'\s+', '_', cleaned)
        
        # Remove multiple underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        
        return cleaned
    
    @staticmethod
    def validate_template(template: str) -> Tuple[bool, List[str]]:
        """
        Validate the template format and return errors.
        
        Args:
            template: Template string to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not template:
            errors.append("Template cannot be empty")
            return False, errors
        
        # Check for at least one variable
        variables = re.findall(r'\{[^}]+\}', template)
        if not variables:
            errors.append("Template must contain at least one variable")
            return False, errors
        
        # Check for valid variable names
        for var in variables:
            var_name = var.strip('{}')
            if var_name not in FilenameUtils.VALID_VARIABLES:
                errors.append(f"Invalid variable '{var_name}'. Valid variables: {', '.join(sorted(FilenameUtils.VALID_VARIABLES))}")
        
        # Check for balanced braces
        if template.count('{') != template.count('}'):
            errors.append("Unbalanced braces in template")
        
        # Check for empty variable names
        if re.search(r'\{\s*\}', template):
            errors.append("Empty variable names are not allowed")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_template_format(template: str) -> bool:
        """
        Internal method to validate template format.
        
        Args:
            template: Template string to validate
            
        Returns:
            True if valid, False otherwise
        """
        is_valid, _ = FilenameUtils.validate_template(template)
        return is_valid
    
    @staticmethod
    def extract_variables_from_template(template: str) -> List[str]:
        """
        Extract variable names from template.
        
        Args:
            template: Template string
            
        Returns:
            List of variable names found in template
        """
        variables = re.findall(r'\{([^}]+)\}', template)
        return [var.strip() for var in variables if var.strip()]
    
    @staticmethod
    def rename_file(old_path: str, new_filename: str, directory: Optional[str] = None) -> str:
        """
        Rename a file with the new filename.
        
        Args:
            old_path: Current file path
            new_filename: New filename (without extension)
            directory: Optional directory to place the file (if None, uses same directory)
            
        Returns:
            New file path
            
        Raises:
            FileNotFoundError: If source file doesn't exist
            OSError: If rename operation fails
        """
        try:
            old_path = Path(old_path)
            if not old_path.exists():
                raise FileNotFoundError(f"Source file not found: {old_path}")
            
            # Preserve original extension
            extension = old_path.suffix
            
            # Determine new directory
            if directory:
                new_dir = Path(directory)
                new_dir.mkdir(parents=True, exist_ok=True)
            else:
                new_dir = old_path.parent
            
            # Create new path
            new_path = new_dir / f"{new_filename}{extension}"
            
            # Handle case where new file already exists
            counter = 1
            original_new_path = new_path
            while new_path.exists():
                new_path = original_new_path.parent / f"{new_filename}_{counter}{extension}"
                counter += 1
            
            # Perform the rename
            shutil.move(str(old_path), str(new_path))
            
            logger.info(f"File renamed: {old_path} -> {new_path}")
            return str(new_path)
            
        except Exception as e:
            logger.error(f"Failed to rename file {old_path}: {e}")
            raise
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        Get a safe filename by cleaning invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        # Remove path separators
        safe_name = os.path.basename(filename)
        
        # Clean invalid characters
        safe_name = FilenameUtils.clean_filename_part(safe_name)
        
        # Ensure it's not empty
        if not safe_name:
            safe_name = "unnamed_file"
        
        return safe_name
    
    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, List[str]]:
        """
        Validate a filename for safety and compatibility.
        
        Args:
            filename: Filename to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not filename:
            errors.append("Filename cannot be empty")
            return False, errors
        
        # Check for invalid characters
        if re.search(FilenameUtils.INVALID_CHARS, filename):
            errors.append("Filename contains invalid characters")
        
        # Check for reserved names (Windows)
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in reserved_names:
            errors.append(f"Filename '{filename}' is a reserved system name")
        
        # Check length (Windows limit is 255 characters for full path)
        if len(filename) > 255:
            errors.append("Filename is too long (max 255 characters)")
        
        # Check for trailing spaces or dots (Windows issue)
        if filename.endswith(' ') or filename.endswith('.'):
            errors.append("Filename cannot end with space or dot")
        
        return len(errors) == 0, errors


class PDFMetadataHandler:
    """Handler for PDF metadata operations related to filename variables."""
    
    METADATA_KEY = "ocr_receipt_variables"
    
    def __init__(self):
        """Initialize the PDF metadata handler."""
        pass
    
    @staticmethod
    def save_variables_to_metadata(pdf_path: str, variables: Dict[str, str]) -> bool:
        """
        Save filename variables to PDF metadata.
        
        Args:
            pdf_path: Path to the PDF file
            variables: Dictionary of variables to save
            
        Returns:
            True if successful, False otherwise
        """
        if not PDF_SUPPORT:
            logger.warning("PDF metadata saving not available - pypdf not installed")
            return False
            
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return False
            
            # Read the existing PDF
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                writer = PdfWriter()
                
                # Copy all pages
                for page in reader.pages:
                    writer.add_page(page)
                
                # Create metadata dictionary with our variables
                metadata = {
                    '/Title': f"OCR Receipt Variables - {Path(pdf_path).name}",
                    '/Creator': 'OCR Receipt Parser',
                    '/Producer': 'OCR Receipt Parser v1.0',
                    '/Subject': 'Invoice/Receipt Data',
                    '/Keywords': json.dumps(variables)  # Store variables as JSON in keywords
                }
                
                # Add metadata to the PDF
                writer.add_metadata(metadata)
            
            # Write the updated PDF
            with open(pdf_path, 'wb') as file:
                writer.write(file)
            
            logger.info(f"Variables saved to PDF metadata: {pdf_path}")
            logger.debug(f"Variables: {variables}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save variables to PDF metadata: {e}")
            return False
    
    @staticmethod
    def load_variables_from_metadata(pdf_path: str) -> Dict[str, str]:
        """
        Load filename variables from PDF metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary of variables found in metadata
        """
        if not PDF_SUPPORT:
            logger.warning("PDF metadata loading not available - pypdf not installed")
            return {}
            
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return {}
            
            # Read the PDF metadata
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                metadata = reader.metadata or {}
                
                # Try to get variables from keywords field
                if '/Keywords' in metadata:
                    try:
                        variables_json = metadata['/Keywords']
                        variables = json.loads(variables_json)
                        logger.info(f"Variables loaded from PDF metadata: {pdf_path}")
                        logger.debug(f"Variables: {variables}")
                        return variables
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"Invalid JSON in PDF keywords metadata: {pdf_path}")
                        return {}
                else:
                    logger.info(f"No variables found in PDF metadata: {pdf_path}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Failed to load variables from PDF metadata: {e}")
            return {}
    
    @staticmethod
    def has_variables_in_metadata(pdf_path: str) -> bool:
        """
        Check if PDF has variables stored in metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if variables are found, False otherwise
        """
        if not PDF_SUPPORT:
            return False
            
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return False
            
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                metadata = reader.metadata or {}
                return '/Keywords' in metadata
                
        except Exception as e:
            logger.error(f"Failed to check PDF metadata: {e}")
            return False


# Convenience functions for backward compatibility
def generate_filename(template: str, data: Dict[str, str]) -> str:
    """Convenience function for filename generation."""
    return FilenameUtils.generate_filename(template, data)


def clean_filename_part(value: str) -> str:
    """Convenience function for cleaning filename parts."""
    return FilenameUtils.clean_filename_part(value)


def validate_template(template: str) -> Tuple[bool, List[str]]:
    """Convenience function for template validation."""
    return FilenameUtils.validate_template(template)


def rename_file(old_path: str, new_filename: str, directory: Optional[str] = None) -> str:
    """Convenience function for file renaming."""
    return FilenameUtils.rename_file(old_path, new_filename, directory) 