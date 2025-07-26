#!/usr/bin/env python3
"""
Simple integration test for multi-language support.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ocr_receipt.utils.translation_helper import set_language, tr, get_language

def test_multi_language_integration():
    """Test the multi-language integration."""
    print("Testing multi-language integration...")
    
    # Test English
    print(f"\n=== Testing English ===")
    set_language('en')
    print(f"Language: {get_language()}")
    print(f"Window title: {tr('main_window.title')}")
    print(f"Add business: {tr('business_keywords_tab.add_business')}")
    print(f"Success: {tr('common.success')}")
    print(f"Error: {tr('common.error')}")
    
    # Test French
    print(f"\n=== Testing French ===")
    set_language('fr')
    print(f"Language: {get_language()}")
    print(f"Window title: {tr('main_window.title')}")
    print(f"Add business: {tr('business_keywords_tab.add_business')}")
    print(f"Success: {tr('common.success')}")
    print(f"Error: {tr('common.error')}")
    
    # Test parameter substitution
    print(f"\n=== Testing Parameter Substitution ===")
    set_language('en')
    print(f"Delete confirm (EN): {tr('business_keywords_tab.delete_confirm', count=3)}")
    
    set_language('fr')
    print(f"Delete confirm (FR): {tr('business_keywords_tab.delete_confirm', count=3)}")
    
    # Test language settings
    print(f"\n=== Testing Language Settings ===")
    set_language('en')
    print(f"Language settings title (EN): {tr('language_settings.title')}")
    
    set_language('fr')
    print(f"Language settings title (FR): {tr('language_settings.title')}")
    
    print("\n✅ Multi-language integration test completed!")

if __name__ == "__main__":
    test_multi_language_integration() 