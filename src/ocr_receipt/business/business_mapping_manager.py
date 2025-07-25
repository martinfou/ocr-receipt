"""
Business Mapping Manager module for OCR Receipt Parser.

Manages business names and keywords for invoice matching, including
exact, variant, and fuzzy matching using FuzzyMatcher.
"""

from typing import List, Dict, Any, Optional, Tuple
from .database_manager import DatabaseManager
from ocr_receipt.core.fuzzy_matcher import FuzzyMatcher

class BusinessMappingManager:
    """
    Manages business names and keywords for invoice matching.
    Integrates with DatabaseManager and FuzzyMatcher.
    """
    def __init__(self, db_manager: DatabaseManager, config: Optional[Dict[str, Any]] = None):
        self.db_manager = db_manager
        self.config = config or {}
        self.fuzzy_matcher = FuzzyMatcher(self.config)
        
        # Initialize database if needed
        try:
            self.db_manager.initialize_database()
        except Exception as e:
            # Log error but don't fail initialization
            print(f"Warning: Database initialization failed: {e}")

    def add_business(self, business_name: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a new business to the database. Returns True if added, False if already exists or error."""
        try:
            # Check if business already exists
            names = self.get_business_names()
            if business_name in names:
                return False
            self.db_manager.add_business(business_name, metadata or {})
            # Automatically add an exact keyword for the business name (case-insensitive by default)
            self.add_keyword(business_name, business_name, is_case_sensitive=0)
            return True
        except Exception as e:
            # Log error
            print(f"Error adding business: {e}")
            return False

    def add_keyword(self, business_name: str, keyword: str, is_case_sensitive: int = 0) -> bool:
        """Add a keyword for a business. Returns True if added, False if error."""
        try:
            # Find business ID
            businesses = self.db_manager.get_all_businesses()
            business = next((b for b in businesses if b["name"] == business_name), None)
            if not business:
                return False
            business_id = business["id"]
            return self.db_manager.add_keyword(business_id, keyword, is_case_sensitive)
        except Exception as e:
            print(f"Error adding keyword: {e}")
            return False

    def get_business_names(self) -> List[str]:
        """Get all business names from the database."""
        try:
            businesses = self.db_manager.get_all_businesses()
            return [b["name"] for b in businesses]
        except Exception as e:
            print(f"Error getting business names: {e}")
            return []

    def get_keywords(self) -> List[Dict[str, Any]]:
        """Get all keywords with business associations."""
        try:
            return self.db_manager.get_all_keywords()
        except Exception as e:
            print(f"Error getting keywords: {e}")
            return []

    def find_business_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """
        Find business match in text using exact and fuzzy matching.
        Returns (business_name, match_type, confidence) or None if no match.
        """
        try:
            keywords = self.get_keywords()
            if not keywords:
                return None
            # 1. Exact match (case sensitive or insensitive)
            for kw in keywords:
                kw_text = kw["keyword"].strip()
                is_case_sensitive = kw.get("is_case_sensitive", 0)
                if is_case_sensitive:
                    if text.strip() == kw_text:
                        return (kw["business_name"], "exact", 1.0)
                    elif text.strip().lower() == kw_text.lower():
                        # Case-insensitive match for case-sensitive keyword, lower score
                        return (kw["business_name"], "exact", 0.8)
                else:
                    if text.strip().lower() == kw_text.lower():
                        return (kw["business_name"], "exact", 1.0)
            
            # 2. Fuzzy match (always attempt if no exact match)
            candidates_insensitive = [kw for kw in keywords if not kw.get("is_case_sensitive", 0)]
            if candidates_insensitive:
                best = self.fuzzy_matcher.find_best_match(text.lower(), [c["keyword"].lower() for c in candidates_insensitive])
                if best:
                    best_keyword, confidence = best
                    for kw in candidates_insensitive:
                        if kw["keyword"].lower() == best_keyword:
                            return (kw["business_name"], "fuzzy", confidence)
            
            candidates_sensitive = [kw for kw in keywords if kw.get("is_case_sensitive", 0)]
            if candidates_sensitive:
                best = self.fuzzy_matcher.find_best_match(text, [c["keyword"] for c in candidates_sensitive])
                if best:
                    best_keyword, confidence = best
                    for kw in candidates_sensitive:
                        if kw["keyword"] == best_keyword:
                            return (kw["business_name"], "fuzzy", confidence)
                # Optionally, try case-insensitive fuzzy for case-sensitive keywords with penalty
                best = self.fuzzy_matcher.find_best_match(text.lower(), [c["keyword"].lower() for c in candidates_sensitive])
                if best:
                    best_keyword, confidence = best
                    for kw in candidates_sensitive:
                        if kw["keyword"].lower() == best_keyword:
                            # Penalize confidence for case-insensitive fuzzy match on case-sensitive keyword
                            return (kw["business_name"], "fuzzy", confidence * 0.8)
            return None
        except Exception as e:
            print(f"Error in find_business_match: {e}")
            return None 