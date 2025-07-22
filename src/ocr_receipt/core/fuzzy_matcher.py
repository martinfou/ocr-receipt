"""
Fuzzy Matcher module for string matching.

This module provides fuzzy string matching functionality for business name matching
and other text comparison tasks in the OCR receipt parser.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from difflib import SequenceMatcher
import re

logger = logging.getLogger(__name__)


class FuzzyMatcherError(Exception):
    """Exception raised for fuzzy matching errors."""
    pass


class FuzzyMatcher:
    """
    Fuzzy string matching for business name matching.
    
    This class provides various fuzzy matching algorithms and utilities
    for comparing strings with different levels of similarity.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the fuzzy matcher.
        
        Args:
            config: Configuration dictionary containing matching settings
        """
        self.config = config
        self._validate_config()
        
        # Matching parameters
        match_config = self.config.get('fuzzy_matching', {})
        self.similarity_threshold = match_config.get('similarity_threshold', 0.8)
        self.case_sensitive = match_config.get('case_sensitive', False)
        self.ignore_punctuation = match_config.get('ignore_punctuation', True)
        self.ignore_whitespace = match_config.get('ignore_whitespace', True)
        self.max_candidates = match_config.get('max_candidates', 10)
        
        logger.info("Fuzzy Matcher initialized")
    
    def _validate_config(self) -> None:
        """Validate the configuration."""
        if not isinstance(self.config, dict):
            raise FuzzyMatcherError("Configuration must be a dictionary")
        
        match_config = self.config.get('fuzzy_matching', {})
        if not isinstance(match_config, dict):
            raise FuzzyMatcherError("Fuzzy matching configuration must be a dictionary")
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings.
        
        Args:
            str1: First string to compare
            str2: Second string to compare
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Preprocess strings
            processed_str1 = self._preprocess_string(str1)
            processed_str2 = self._preprocess_string(str2)
            
            # Calculate similarity using SequenceMatcher
            similarity = SequenceMatcher(None, processed_str1, processed_str2).ratio()
            
            return similarity
            
        except Exception as e:
            logger.warning(f"Similarity calculation failed: {e}")
            return 0.0
    
    def find_best_match(self, query: str, candidates: List[str]) -> Optional[Tuple[str, float]]:
        """
        Find the best matching candidate for a query string.
        
        Args:
            query: Query string to match
            candidates: List of candidate strings to match against
            
        Returns:
            Tuple of (best_match, similarity_score) or None if no match above threshold
        """
        try:
            if not candidates:
                return None
            
            best_match = None
            best_similarity = 0.0
            
            for candidate in candidates:
                similarity = self.calculate_similarity(query, candidate)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = candidate
            
            # Return only if similarity meets threshold
            if best_similarity >= self.similarity_threshold:
                return (best_match, best_similarity)
            
            return None
            
        except Exception as e:
            logger.error(f"Best match finding failed: {e}")
            return None
    
    def find_all_matches(self, query: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """
        Find all candidates that match the query above the threshold.
        
        Args:
            query: Query string to match
            candidates: List of candidate strings to match against
            
        Returns:
            List of tuples (candidate, similarity_score) sorted by similarity
        """
        try:
            if not candidates:
                return []
            
            matches = []
            
            for candidate in candidates:
                similarity = self.calculate_similarity(query, candidate)
                if similarity >= self.similarity_threshold:
                    matches.append((candidate, similarity))
            
            # Sort by similarity (highest first)
            matches.sort(key=lambda x: x[1], reverse=True)
            
            # Limit to max candidates
            return matches[:self.max_candidates]
            
        except Exception as e:
            logger.error(f"All matches finding failed: {e}")
            return []
    
    def is_similar(self, str1: str, str2: str) -> bool:
        """
        Check if two strings are similar above the threshold.
        
        Args:
            str1: First string to compare
            str2: Second string to compare
            
        Returns:
            True if strings are similar above threshold, False otherwise
        """
        try:
            similarity = self.calculate_similarity(str1, str2)
            return similarity >= self.similarity_threshold
            
        except Exception as e:
            logger.warning(f"Similarity check failed: {e}")
            return False
    
    def normalize_string(self, text: str) -> str:
        """
        Normalize a string for better matching.
        
        Args:
            text: String to normalize
            
        Returns:
            Normalized string
        """
        try:
            normalized = text
            
            # Convert to lowercase if not case sensitive
            if not self.case_sensitive:
                normalized = normalized.lower()
            
            # Remove punctuation if enabled
            if self.ignore_punctuation:
                normalized = re.sub(r'[^\w\s]', '', normalized)
            
            # Normalize whitespace if enabled
            if self.ignore_whitespace:
                normalized = re.sub(r'\s+', ' ', normalized).strip()
            
            return normalized
            
        except Exception as e:
            logger.warning(f"String normalization failed: {e}")
            return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text for matching.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of keywords
        """
        try:
            # Normalize the text
            normalized = self.normalize_string(text)
            
            # Split into words
            words = normalized.split()
            
            # Filter out common stop words (basic implementation)
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            keywords = [word for word in words if word not in stop_words and len(word) > 2]
            
            return keywords
            
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            return []
    
    def calculate_keyword_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """
        Calculate similarity based on keyword overlap.
        
        Args:
            keywords1: First list of keywords
            keywords2: Second list of keywords
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            if not keywords1 or not keywords2:
                return 0.0
            
            # Convert to sets for intersection calculation
            set1 = set(keywords1)
            set2 = set(keywords2)
            
            # Calculate Jaccard similarity
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception as e:
            logger.warning(f"Keyword similarity calculation failed: {e}")
            return 0.0
    
    def find_keyword_matches(self, query: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """
        Find matches based on keyword similarity.
        
        Args:
            query: Query string to match
            candidates: List of candidate strings to match against
            
        Returns:
            List of tuples (candidate, similarity_score) sorted by similarity
        """
        try:
            if not candidates:
                return []
            
            # Extract keywords from query
            query_keywords = self.extract_keywords(query)
            
            matches = []
            
            for candidate in candidates:
                # Extract keywords from candidate
                candidate_keywords = self.extract_keywords(candidate)
                
                # Calculate keyword similarity
                keyword_similarity = self.calculate_keyword_similarity(query_keywords, candidate_keywords)
                
                # Calculate overall similarity
                overall_similarity = self.calculate_similarity(query, candidate)
                
                # Combine similarities (weighted average)
                combined_similarity = (keyword_similarity * 0.6) + (overall_similarity * 0.4)
                
                if combined_similarity >= self.similarity_threshold:
                    matches.append((candidate, combined_similarity))
            
            # Sort by similarity (highest first)
            matches.sort(key=lambda x: x[1], reverse=True)
            
            # Limit to max candidates
            return matches[:self.max_candidates]
            
        except Exception as e:
            logger.error(f"Keyword matching failed: {e}")
            return []
    
    def _preprocess_string(self, text: str) -> str:
        """
        Preprocess a string for matching.
        
        Args:
            text: String to preprocess
            
        Returns:
            Preprocessed string
        """
        try:
            if not text:
                return ""
            
            # Normalize the string
            processed = self.normalize_string(text)
            
            return processed
            
        except Exception as e:
            logger.warning(f"String preprocessing failed: {e}")
            return text
    
    def get_matching_statistics(self, query: str, candidates: List[str]) -> Dict[str, Any]:
        """
        Get statistics about matching results.
        
        Args:
            query: Query string to match
            candidates: List of candidate strings to match against
            
        Returns:
            Dictionary containing matching statistics
        """
        try:
            if not candidates:
                return {
                    'total_candidates': 0,
                    'matches_found': 0,
                    'average_similarity': 0.0,
                    'max_similarity': 0.0,
                    'min_similarity': 0.0
                }
            
            # Calculate similarities for all candidates
            similarities = []
            for candidate in candidates:
                similarity = self.calculate_similarity(query, candidate)
                similarities.append(similarity)
            
            # Calculate statistics
            matches_found = len([s for s in similarities if s >= self.similarity_threshold])
            average_similarity = sum(similarities) / len(similarities) if similarities else 0.0
            max_similarity = max(similarities) if similarities else 0.0
            min_similarity = min(similarities) if similarities else 0.0
            
            stats = {
                'total_candidates': len(candidates),
                'matches_found': matches_found,
                'average_similarity': average_similarity,
                'max_similarity': max_similarity,
                'min_similarity': min_similarity,
                'similarity_distribution': {
                    'high': len([s for s in similarities if s >= 0.9]),
                    'medium': len([s for s in similarities if 0.7 <= s < 0.9]),
                    'low': len([s for s in similarities if 0.5 <= s < 0.7]),
                    'very_low': len([s for s in similarities if s < 0.5])
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Matching statistics calculation failed: {e}")
            return {} 