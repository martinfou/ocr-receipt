"""
Date Extractor module for parsing dates from text.

This module provides functionality to extract and parse dates from text
using various formats and languages.
"""

import logging
import re
from datetime import datetime
from typing import List, Optional, Tuple
import unicodedata

from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class DateExtractorError(Exception):
    """Exception raised for date extraction errors."""
    pass


class DateExtractor:
    """
    Date extractor for parsing dates from text.
    
    This class provides functionality to extract dates from text using
    various formats and languages, with support for French month names.
    """
    
    def __init__(self):
        """Initialize the date extractor."""
        # French month mappings (normalized)
        self.french_months = {
            'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12
        }
        
        # English month mappings
        self.english_months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        logger.info("DateExtractor initialized")
    
    def extract_date(self, text: str) -> Optional[str]:
        """
        Extract a date from text and return it in ISO format (YYYY-MM-DD).
        
        Args:
            text: Text containing a date
            
        Returns:
            Date in ISO format (YYYY-MM-DD) or None if no date found
            
        Raises:
            DateExtractorError: If date extraction fails
        """
        try:
            if not text or not text.strip():
                return None
            
            # First try to find date patterns in the text
            date_matches = self._find_date_patterns(text)
            
            if not date_matches:
                return None
            
            # Try to parse each match
            for match in date_matches:
                try:
                    parsed_date = self._parse_date_string(match)
                    if parsed_date:
                        return parsed_date.strftime("%Y-%m-%d")
                except Exception as e:
                    logger.debug(f"Failed to parse date match '{match}': {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Date extraction failed: {e}")
            raise DateExtractorError(f"Date extraction failed: {e}")
    
    def extract_all_dates(self, text: str) -> List[str]:
        """
        Extract all dates from text and return them in ISO format.
        
        Args:
            text: Text containing dates
            
        Returns:
            List of dates in ISO format (YYYY-MM-DD)
            
        Raises:
            DateExtractorError: If date extraction fails
        """
        try:
            if not text or not text.strip():
                return []
            
            # Find all date patterns
            date_matches = self._find_date_patterns(text)
            
            if not date_matches:
                return []
            
            # Parse each match
            parsed_dates = []
            for match in date_matches:
                try:
                    parsed_date = self._parse_date_string(match)
                    if parsed_date:
                        date_str = parsed_date.strftime("%Y-%m-%d")
                        if date_str not in parsed_dates:  # Avoid duplicates
                            parsed_dates.append(date_str)
                    else:
                        continue
                except Exception as e:
                    logger.debug(f"Failed to parse date match '{match}': {e}")
                    continue
            
            return parsed_dates
            
        except Exception as e:
            logger.error(f"Date extraction failed: {e}")
            raise DateExtractorError(f"Date extraction failed: {e}")
    
    def validate_date(self, date_str: str) -> bool:
        """
        Validate if a date string is in ISO format (YYYY-MM-DD).
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid ISO date, False otherwise
        """
        try:
            if not date_str or not isinstance(date_str, str):
                return False
            
            # Check format with regex
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                return False
            
            # Try to parse the date
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
            
        except Exception:
            return False
    
    def _find_date_patterns(self, text: str) -> List[str]:
        """
        Find potential date patterns in text.
        
        Args:
            text: Text to search for dates
            
        Returns:
            List of potential date strings
        """
        patterns = [
            # ISO format: 2024-06-01 or 2024/06/01
            r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
            # US format: 06/01/2024 or 6/1/2024
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b',
            # Day Month Year: 1 June 2024, 01 juin 2024
            r'\b\d{1,2}\s+[A-Za-zÀ-ÿ]{3,15}\s+\d{4}\b',
            # Month Day Year: June 1, 2024, juin 1, 2024
            r'\b[A-Za-zÀ-ÿ]{3,15}\s+\d{1,2},?\s*\d{4}\b',
            # Various other formats
            r'\b\d{1,2}\.\d{1,2}\.\d{4}\b',  # DD.MM.YYYY
            r'\b\d{4}\.\d{1,2}\.\d{1,2}\b',  # YYYY.MM.DD
        ]
        
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.extend(found)
        
        return list(set(matches))  # Remove duplicates
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """
        Parse a date string using dateutil parser with custom handling.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Parsed datetime object or None if parsing fails
        """
        try:
            # Normalize the date string
            normalized_str = self._normalize_date_string(date_str)
            
            # Determine parsing strategy based on format
            if re.match(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}$', normalized_str):
                # YYYY-MM-DD or YYYY/MM/DD format - use year-first
                parsed_date = date_parser.parse(normalized_str, dayfirst=False, yearfirst=True)
            elif re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{4}$', normalized_str):
                # DD/MM/YYYY or MM/DD/YYYY format - prefer day-first for European format
                parsed_date = date_parser.parse(normalized_str, dayfirst=True, yearfirst=False)
            else:
                # Other formats (with month names, etc.) - use default parsing
                parsed_date = date_parser.parse(normalized_str, dayfirst=False, yearfirst=False)
            
            # Validate the parsed date (should be reasonable)
            if parsed_date.year < 1900 or parsed_date.year > 2100:
                logger.debug(f"Parsed date year {parsed_date.year} is out of reasonable range")
                return None
            
            return parsed_date
            
        except Exception as e:
            logger.debug(f"Failed to parse date string '{date_str}': {e}")
            return None
    
    def _normalize_date_string(self, date_str: str) -> str:
        """
        Normalize a date string for better parsing.
        
        Args:
            date_str: Date string to normalize
            
        Returns:
            Normalized date string
        """
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', date_str.strip())
        
        # Handle French month names
        normalized = self._replace_french_months(normalized)
        
        # Handle common separators
        normalized = re.sub(r'[,\s]+', ' ', normalized)
        
        return normalized
    
    def _replace_french_months(self, text: str) -> str:
        """
        Replace French month names with English equivalents.
        
        Args:
            text: Text containing French month names
            
        Returns:
            Text with French months replaced by English equivalents
        """
        # Normalize text (remove accents)
        normalized_text = unicodedata.normalize('NFD', text.lower())
        normalized_text = ''.join(c for c in normalized_text if not unicodedata.combining(c))
        
        # Replace French months with English equivalents
        french_to_english = {
            'janvier': 'january',
            'fevrier': 'february', 
            'mars': 'march',
            'avril': 'april',
            'mai': 'may',
            'juin': 'june',
            'juillet': 'july',
            'aout': 'august',
            'septembre': 'september',
            'octobre': 'october',
            'novembre': 'november',
            'decembre': 'december'
        }
        
        for french, english in french_to_english.items():
            normalized_text = re.sub(r'\b' + french + r'\b', english, normalized_text, flags=re.IGNORECASE)
        
        return normalized_text 