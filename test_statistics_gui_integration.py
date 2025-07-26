#!/usr/bin/env python3
"""
Simple test to verify statistics GUI integration.
"""

import sys
import tempfile
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager
from ocr_receipt.gui.business_keywords_tab import BusinessKeywordsTab
from ocr_receipt.gui.widgets.statistics_panel import StatisticsPanel

def test_statistics_integration():
    """Test that statistics integrate correctly with the GUI."""
    print("Testing statistics GUI integration...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Setup database and managers
        db_manager = DatabaseManager(db_path)
        business_mapping_manager = BusinessMappingManager(db_manager)
        
        # Add test data
        print("Adding test businesses and keywords...")
        business_mapping_manager.add_business("Test Business 1")
        business_mapping_manager.add_business("Test Business 2")
        
        business_mapping_manager.add_keyword("Test Business 1", "keyword1", 0)
        business_mapping_manager.add_keyword("Test Business 1", "keyword2", 1)
        business_mapping_manager.add_keyword("Test Business 2", "keyword3", 0)
        
        # Simulate usage
        print("Simulating keyword usage...")
        db_manager.execute_query(
            "UPDATE business_keywords SET usage_count = 15, last_used = '2024-01-16 10:00:00' WHERE keyword = 'keyword1'"
        )
        db_manager.execute_query(
            "UPDATE business_keywords SET usage_count = 8, last_used = '2024-01-15 10:00:00' WHERE keyword = 'keyword2'"
        )
        db_manager.execute_query(
            "UPDATE business_keywords SET usage_count = 22, last_used = '2024-01-17 10:00:00' WHERE keyword = 'keyword3'"
        )
        
        # Get statistics
        print("Getting comprehensive statistics...")
        stats = business_mapping_manager.get_comprehensive_statistics()
        
        print(f"Statistics summary:")
        print(f"  Total businesses: {stats['keywords']['total_businesses']}")
        print(f"  Total keywords: {stats['keywords']['total_keywords']}")
        print(f"  Total usage: {stats['keywords']['total_usage']}")
        print(f"  Keyword efficiency: {stats['performance']['keyword_efficiency']}%")
        
        # Test statistics panel
        print("Testing StatisticsPanel widget...")
        app = QApplication([])
        
        statistics_panel = StatisticsPanel()
        statistics_panel.load_statistics(stats)
        
        # Verify data is loaded
        assert statistics_panel.most_used_table.rowCount() == 3
        assert statistics_panel.most_used_table.item(0, 0).text() == 'keyword3'  # Highest usage
        
        print("✓ StatisticsPanel loaded data correctly")
        
        # Test business keywords tab integration
        print("Testing BusinessKeywordsTab integration...")
        tab = BusinessKeywordsTab(business_mapping_manager)
        
        # Verify statistics are loaded
        assert tab.statistics_panel is not None
        assert tab.statistics_panel.most_used_table.rowCount() == 3
        
        print("✓ BusinessKeywordsTab integrated statistics correctly")
        
        print("\n🎉 All statistics integration tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        # Cleanup
        db_manager.close()
        os.unlink(db_path)

if __name__ == "__main__":
    test_statistics_integration() 