"""
Business Mapping Manager module for OCR Receipt Parser.

Manages business names and keywords for invoice matching, including
exact, variant, and fuzzy matching using FuzzyMatcher.
"""

from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from .database_manager import DatabaseManager
from ocr_receipt.core.fuzzy_matcher import FuzzyMatcher

class BusinessMappingManager(QObject):
    """
    Manages business names and keywords for invoice matching.
    Integrates with DatabaseManager and FuzzyMatcher.
    """
    # Signals for UI updates
    business_added = pyqtSignal(str)  # Emits business name when added
    business_updated = pyqtSignal(str, str)  # Emits old_name, new_name when updated
    business_deleted = pyqtSignal(str)  # Emits business name when deleted
    keyword_added = pyqtSignal(str, str)  # Emits business_name, keyword when keyword added
    keyword_updated = pyqtSignal(str, str, str)  # Emits business_name, old_keyword, new_keyword when updated
    keyword_deleted = pyqtSignal(str, str)  # Emits business_name, keyword when deleted
    
    def __init__(self, db_manager: DatabaseManager, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.db_manager = db_manager
        self.config = config or {}
        self.fuzzy_matcher = FuzzyMatcher(self.config)
        
        # Initialize database if needed
        try:
            self.db_manager.initialize_database()
        except Exception as e:
            # Log error but don't fail initialization
            print(f"Warning: Database initialization failed: {e}")

    def add_business(self, business_name: str, metadata: Optional[Dict[str, Any]] = None, match_type: str = "exact") -> bool:
        """Add a new business to the database. Returns True if added, False if already exists or error."""
        try:
            # Check if business already exists
            names = self.get_business_names()
            if business_name in names:
                return False
            self.db_manager.add_business(business_name, metadata or {})
            # Automatically add a keyword for the business name with the specified match type (case-insensitive by default)
            self.add_keyword(business_name, business_name, is_case_sensitive=0, match_type=match_type)
            # Emit signal for UI updates
            self.business_added.emit(business_name)
            return True
        except Exception as e:
            # Log error
            print(f"Error adding business: {e}")
            return False

    def add_keyword(self, business_name: str, keyword: str, is_case_sensitive: int = 0, match_type: str = "exact") -> bool:
        """Add a keyword for a business. Returns True if added, False if error."""
        try:
            # Find business ID efficiently
            business = self.db_manager.get_business_by_name(business_name)
            if not business:
                return False
            business_id = business["id"]
            success = self.db_manager.add_keyword(business_id, keyword, is_case_sensitive, match_type)
            if success:
                # Emit signal for UI updates
                self.keyword_added.emit(business_name, keyword)
            return success
        except Exception as e:
            print(f"Error adding keyword: {e}")
            return False

    def update_keyword(self, business_name: str, old_keyword: str, new_keyword: str, is_case_sensitive: int, match_type: str = "exact") -> bool:
        """Update a keyword for a business. Returns True if updated, False if error."""
        try:
            # Find business ID efficiently
            business = self.db_manager.get_business_by_name(business_name)
            if not business:
                return False
            business_id = business["id"]
            success = self.db_manager.update_keyword(business_id, old_keyword, new_keyword, is_case_sensitive, match_type)
            if success:
                # Emit signal for UI updates
                self.keyword_updated.emit(business_name, old_keyword, new_keyword)
            return success
        except Exception as e:
            print(f"Error updating keyword: {e}")
            return False

    def update_business_and_keyword(self, old_business_name: str, new_business_name: str, old_keyword: str, new_keyword: str, is_case_sensitive: int, match_type: str = "exact") -> bool:
        """
        Update both business name and keyword in a single operation.
        Returns True if updated, False if error.
        """
        try:
            # Find the original business
            old_business = self.db_manager.get_business_by_name(old_business_name)
            if not old_business:
                return False
            
            old_business_id = old_business["id"]
            
            # Check if new business name already exists (and it's different from old)
            if new_business_name != old_business_name:
                existing_business = self.db_manager.get_business_by_name(new_business_name)
                if existing_business:
                    return False  # New business name already exists
            
            # Update the business name first
            if new_business_name != old_business_name:
                success = self.db_manager.update_business_name(old_business_id, new_business_name)
                if not success:
                    return False
                # Emit signal for business update
                self.business_updated.emit(old_business_name, new_business_name)
            
            # Update the keyword
            success = self.db_manager.update_keyword(old_business_id, old_keyword, new_keyword, is_case_sensitive, match_type)
            if success:
                # Emit signal for keyword update
                self.keyword_updated.emit(new_business_name, old_keyword, new_keyword)
            return success
        except Exception as e:
            print(f"Error updating business and keyword: {e}")
            return False

    def delete_keyword(self, business_name: str, keyword: str) -> bool:
        """Delete a keyword for a business. Returns True if deleted, False if error."""
        try:
            # Find business ID efficiently
            business = self.db_manager.get_business_by_name(business_name)
            if not business:
                return False
            business_id = business["id"]
            success = self.db_manager.delete_keyword(business_id, keyword)
            if success:
                # Emit signal for UI updates
                self.keyword_deleted.emit(business_name, keyword)
            return success
        except Exception as e:
            print(f"Error deleting keyword: {e}")
            return False

    def is_last_keyword_for_business(self, business_name: str, keyword: str) -> bool:
        """Check if this is the last keyword for the business."""
        try:
            keywords = self.get_keywords_for_business(business_name)
            return len(keywords) == 1 and keywords[0]['keyword'] == keyword
        except Exception as e:
            print(f"Error checking if last keyword for business {business_name}: {e}")
            return False

    def delete_business(self, business_name: str) -> bool:
        """Delete a business and all its keywords. Returns True if deleted, False if error."""
        try:
            # Find business ID efficiently
            business = self.db_manager.get_business_by_name(business_name)
            if not business:
                return False
            business_id = business["id"]
            
            # First, delete all keywords for this business
            keywords = self.db_manager.get_all_keywords()
            business_keywords = [k for k in keywords if k['business_name'] == business_name]
            
            for keyword in business_keywords:
                self.db_manager.delete_keyword(business_id, keyword['keyword'])
            
            # Then delete the business
            query = "DELETE FROM businesses WHERE id = ?"
            self.db_manager.execute_query(query, (business_id,))
            
            # Emit signal for UI updates
            self.business_deleted.emit(business_name)
            return True
        except Exception as e:
            print(f"Error deleting business: {e}")
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

    def get_keywords_for_business(self, business_name: str) -> List[Dict[str, Any]]:
        """Get all keywords for a specific business."""
        try:
            keywords = self.get_keywords()
            return [kw for kw in keywords if kw['business_name'] == business_name]
        except Exception as e:
            print(f"Error getting keywords for business {business_name}: {e}")
            return []

    def get_keyword_count_for_business(self, business_name: str) -> int:
        """Get the number of keywords for a specific business."""
        try:
            keywords = self.get_keywords_for_business(business_name)
            return len(keywords)
        except Exception as e:
            print(f"Error getting keyword count for business {business_name}: {e}")
            return 0

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

    def get_keyword_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive keyword statistics for reporting.
        :return: Dictionary containing various statistics
        """
        try:
            return self.db_manager.get_keyword_statistics()
        except Exception as e:
            print(f"Error getting keyword statistics: {e}")
            return {}

    def get_business_statistics(self) -> Dict[str, Any]:
        """
        Get business-specific statistics for reporting.
        :return: Dictionary containing business statistics
        """
        try:
            return self.db_manager.get_business_statistics()
        except Exception as e:
            print(f"Error getting business statistics: {e}")
            return {}

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance and efficiency metrics for reporting.
        :return: Dictionary containing performance metrics
        """
        try:
            return self.db_manager.get_performance_metrics()
        except Exception as e:
            print(f"Error getting performance metrics: {e}")
            return {}

    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """
        Get all statistics in one call for comprehensive reporting.
        :return: Dictionary containing all statistics
        """
        try:
            stats = {}
            stats['keywords'] = self.get_keyword_statistics()
            stats['businesses'] = self.get_business_statistics()
            stats['performance'] = self.get_performance_metrics()
            return stats
        except Exception as e:
            print(f"Error getting comprehensive statistics: {e}")
            return {} 