"""
Unit tests for statistics functionality in OCR Receipt Parser.

Tests the statistics methods in DatabaseManager, BusinessMappingManager,
and the StatisticsPanel widget.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from PyQt6.QtCore import Qt

from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager
from ocr_receipt.gui.widgets.statistics_panel import StatisticsPanel


class TestDatabaseManagerStatistics:
    """Test statistics methods in DatabaseManager."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a temporary database manager for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db_manager = DatabaseManager(db_path)
        db_manager.initialize_database()
        
        # Add test data
        business1_id = db_manager.add_business("Test Business 1")
        business2_id = db_manager.add_business("Test Business 2")
        
        # Add keywords with usage data
        db_manager.add_keyword(business1_id, "keyword1", 0)
        db_manager.add_keyword(business1_id, "keyword2", 1)
        db_manager.add_keyword(business2_id, "keyword3", 0)
        db_manager.add_keyword(business2_id, "keyword4", 0)
        
        # Update usage counts (simulate usage)
        db_manager.execute_query(
            "UPDATE business_keywords SET usage_count = 10, last_used = '2024-01-15 10:00:00' WHERE keyword = 'keyword1'"
        )
        db_manager.execute_query(
            "UPDATE business_keywords SET usage_count = 5, last_used = '2024-01-14 10:00:00' WHERE keyword = 'keyword2'"
        )
        db_manager.execute_query(
            "UPDATE business_keywords SET usage_count = 20, last_used = '2024-01-16 10:00:00' WHERE keyword = 'keyword3'"
        )
        # keyword4 remains unused
        
        yield db_manager
        
        # Cleanup
        db_manager.close()
        os.unlink(db_path)
    
    def test_get_keyword_statistics(self, db_manager):
        """Test getting comprehensive keyword statistics."""
        stats = db_manager.get_keyword_statistics()
        
        assert isinstance(stats, dict)
        assert stats['total_businesses'] == 2
        assert stats['total_keywords'] == 4
        assert stats['case_sensitive_keywords'] == 1
        assert stats['case_insensitive_keywords'] == 3
        assert stats['total_usage'] == 35
        assert stats['average_usage'] == 8.75
        assert stats['max_usage'] == 20
        
        # Check most used keywords
        most_used = stats['most_used_keywords']
        assert len(most_used) == 3  # Only keywords with usage > 0
        assert most_used[0]['keyword'] == 'keyword3'  # Highest usage
        assert most_used[0]['usage_count'] == 20
        
        # Check recently used keywords
        recent = stats['recently_used_keywords']
        assert len(recent) == 3
        assert recent[0]['keyword'] == 'keyword3'  # Most recent
        
        # Check unused keywords
        unused = stats['unused_keywords']
        assert len(unused) == 1
        assert unused[0]['keyword'] == 'keyword4'
        
        # Check usage ranges
        usage_ranges = stats['keywords_by_usage_range']
        assert len(usage_ranges) == 3  # Never Used, Low Usage, High Usage
        never_used = next(r for r in usage_ranges if r['usage_range'] == 'Never Used')
        assert never_used['count'] == 1
    
    def test_get_business_statistics(self, db_manager):
        """Test getting business-specific statistics."""
        stats = db_manager.get_business_statistics()
        
        assert isinstance(stats, dict)
        
        # Check businesses by total usage
        by_usage = stats['businesses_by_total_usage']
        assert len(by_usage) == 2
        assert by_usage[0]['business_name'] == 'Test Business 2'  # Higher total usage
        assert by_usage[0]['total_usage'] == 20
        
        # Check businesses by recent activity
        by_recent = stats['businesses_by_recent_activity']
        assert len(by_recent) == 2
        assert by_recent[0]['business_name'] == 'Test Business 2'  # Most recent activity
        
        # Check businesses by average usage
        by_avg = stats['businesses_by_avg_usage']
        assert len(by_avg) == 2
        assert by_avg[0]['business_name'] == 'Test Business 2'  # Higher average usage
    
    def test_get_performance_metrics(self, db_manager):
        """Test getting performance metrics."""
        metrics = db_manager.get_performance_metrics()
        
        assert isinstance(metrics, dict)
        assert metrics['keyword_efficiency'] == 75.0  # 3 out of 4 keywords used
        assert metrics['avg_keywords_per_business'] == 2.0  # 4 keywords / 2 businesses
        
        # Check most efficient keywords
        efficient = metrics['most_efficient_keywords']
        assert len(efficient) == 3
        assert efficient[0]['keyword'] == 'keyword3'  # Highest usage
    
    def test_statistics_with_empty_database(self):
        """Test statistics methods with empty database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db_manager = DatabaseManager(db_path)
        db_manager.initialize_database()
        
        try:
            stats = db_manager.get_keyword_statistics()
            assert stats['total_businesses'] == 0
            assert stats['total_keywords'] == 0
            assert stats['total_usage'] == 0
            assert stats['average_usage'] == 0
            assert stats['max_usage'] == 0
            
            business_stats = db_manager.get_business_statistics()
            assert business_stats['businesses_by_total_usage'] == []
            assert business_stats['businesses_by_recent_activity'] == []
            
            metrics = db_manager.get_performance_metrics()
            assert metrics['keyword_efficiency'] == 0
            assert metrics['avg_keywords_per_business'] == 0
            
        finally:
            db_manager.close()
            os.unlink(db_path)


class TestBusinessMappingManagerStatistics:
    """Test statistics methods in BusinessMappingManager."""
    
    @pytest.fixture
    def business_mapping_manager(self):
        """Create a business mapping manager with test data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db_manager = DatabaseManager(db_path)
        business_mapping_manager = BusinessMappingManager(db_manager)
        
        # Add test data
        business_mapping_manager.add_business("Test Business 1")
        business_mapping_manager.add_business("Test Business 2")
        
        # Add keywords
        business_mapping_manager.add_keyword("Test Business 1", "keyword1", 0)
        business_mapping_manager.add_keyword("Test Business 1", "keyword2", 1)
        business_mapping_manager.add_keyword("Test Business 2", "keyword3", 0)
        
        yield business_mapping_manager
        
        # Cleanup
        db_manager.close()
        os.unlink(db_path)
    
    def test_get_keyword_statistics(self, business_mapping_manager):
        """Test getting keyword statistics through business mapping manager."""
        stats = business_mapping_manager.get_keyword_statistics()
        
        assert isinstance(stats, dict)
        assert stats['total_businesses'] == 2
        assert stats['total_keywords'] == 5  # 3 manual + 2 automatic (one per business)
        assert stats['case_sensitive_keywords'] == 1
        assert stats['case_insensitive_keywords'] == 4  # 2 manual + 2 automatic
    
    def test_get_business_statistics(self, business_mapping_manager):
        """Test getting business statistics through business mapping manager."""
        stats = business_mapping_manager.get_business_statistics()
        
        assert isinstance(stats, dict)
        assert 'businesses_by_total_usage' in stats
        assert 'businesses_by_recent_activity' in stats
        assert 'businesses_by_avg_usage' in stats
    
    def test_get_performance_metrics(self, business_mapping_manager):
        """Test getting performance metrics through business mapping manager."""
        metrics = business_mapping_manager.get_performance_metrics()
        
        assert isinstance(metrics, dict)
        assert 'keyword_efficiency' in metrics
        assert 'avg_keywords_per_business' in metrics
        assert 'most_efficient_keywords' in metrics
    
    def test_get_comprehensive_statistics(self, business_mapping_manager):
        """Test getting all statistics in one call."""
        stats = business_mapping_manager.get_comprehensive_statistics()
        
        assert isinstance(stats, dict)
        assert 'keywords' in stats
        assert 'businesses' in stats
        assert 'performance' in stats
        
        assert isinstance(stats['keywords'], dict)
        assert isinstance(stats['businesses'], dict)
        assert isinstance(stats['performance'], dict)


class TestStatisticsPanel:
    """Test the StatisticsPanel widget."""
    
    @pytest.fixture
    def statistics_panel(self, qapp, qtbot):
        """Create a StatisticsPanel widget."""
        panel = StatisticsPanel()
        qtbot.addWidget(panel)
        return panel
    
    def test_statistics_panel_creation(self, statistics_panel):
        """Test that the statistics panel is created correctly."""
        assert statistics_panel is not None
        assert statistics_panel.tab_widget is not None
        assert statistics_panel.tab_widget.count() == 4  # Overview, Keyword Stats, Business Stats, Performance
        
        # Check that all tables exist
        assert statistics_panel.most_used_table is not None
        assert statistics_panel.recent_table is not None
        assert statistics_panel.usage_table is not None
        assert statistics_panel.business_usage_table is not None
        assert statistics_panel.business_keyword_count_table is not None
        assert statistics_panel.business_avg_usage_table is not None
        assert statistics_panel.efficient_table is not None
        assert statistics_panel.unused_table is not None
    
    def test_load_statistics(self, statistics_panel):
        """Test loading statistics data into the panel."""
        test_stats = {
            'keywords': {
                'total_businesses': 5,
                'total_keywords': 15,
                'total_usage': 100,
                'case_sensitive_keywords': 3,
                'case_insensitive_keywords': 12,
                'average_usage': 6.67,
                'max_usage': 25,
                'most_used_keywords': [
                    {'keyword': 'test1', 'usage_count': 25, 'business_name': 'Business 1'},
                    {'keyword': 'test2', 'usage_count': 20, 'business_name': 'Business 2'}
                ],
                'recently_used_keywords': [
                    {'keyword': 'test1', 'last_used': '2024-01-16', 'business_name': 'Business 1'},
                    {'keyword': 'test2', 'last_used': '2024-01-15', 'business_name': 'Business 2'}
                ],
                'keywords_by_usage_range': [
                    {'usage_range': 'Never Used', 'count': 5},
                    {'usage_range': 'Low Usage (1-5)', 'count': 8},
                    {'usage_range': 'High Usage (21-50)', 'count': 2}
                ],
                'businesses_by_keyword_count': [
                    {'business_name': 'Business 1', 'keyword_count': 8},
                    {'business_name': 'Business 2', 'keyword_count': 7}
                ],
                'unused_keywords': [
                    {'keyword': 'unused1', 'business_name': 'Business 1'},
                    {'keyword': 'unused2', 'business_name': 'Business 2'}
                ]
            },
            'businesses': {
                'businesses_by_total_usage': [
                    {'business_name': 'Business 1', 'total_usage': 60},
                    {'business_name': 'Business 2', 'total_usage': 40}
                ],
                'businesses_by_avg_usage': [
                    {'business_name': 'Business 1', 'keyword_count': 8, 'avg_usage_per_keyword': 7.5},
                    {'business_name': 'Business 2', 'keyword_count': 7, 'avg_usage_per_keyword': 5.7}
                ]
            },
            'performance': {
                'keyword_efficiency': 66.67,
                'avg_keywords_per_business': 3.0,
                'most_efficient_keywords': [
                    {'keyword': 'test1', 'usage_count': 25, 'business_name': 'Business 1'},
                    {'keyword': 'test2', 'usage_count': 20, 'business_name': 'Business 2'}
                ]
            }
        }
        
        # Load statistics
        statistics_panel.load_statistics(test_stats)
        
        # Check that tables are populated
        assert statistics_panel.most_used_table.rowCount() == 2
        assert statistics_panel.recent_table.rowCount() == 2
        assert statistics_panel.usage_table.rowCount() == 3
        assert statistics_panel.business_usage_table.rowCount() == 2
        assert statistics_panel.business_keyword_count_table.rowCount() == 2
        assert statistics_panel.business_avg_usage_table.rowCount() == 2
        assert statistics_panel.efficient_table.rowCount() == 2
        assert statistics_panel.unused_table.rowCount() == 2
        
        # Check specific values
        assert statistics_panel.most_used_table.item(0, 0).text() == 'test1'
        assert statistics_panel.most_used_table.item(0, 1).text() == '25'
        assert statistics_panel.most_used_table.item(0, 2).text() == 'Business 1'
    
    def test_load_empty_statistics(self, statistics_panel):
        """Test loading empty statistics data."""
        empty_stats = {
            'keywords': {},
            'businesses': {},
            'performance': {}
        }
        
        # Should not raise any exceptions
        statistics_panel.load_statistics(empty_stats)
        
        # Tables should be empty
        assert statistics_panel.most_used_table.rowCount() == 0
        assert statistics_panel.recent_table.rowCount() == 0
        assert statistics_panel.usage_table.rowCount() == 0
    
    def test_refresh_button(self, statistics_panel):
        """Test that refresh button exists and is connected."""
        assert statistics_panel.refresh_button is not None
        assert statistics_panel.refresh_button.text() == "Refresh Statistics"
    
    def test_table_readonly(self, statistics_panel):
        """Test that all tables are read-only."""
        test_stats = {
            'keywords': {
                'most_used_keywords': [{'keyword': 'test', 'usage_count': 10, 'business_name': 'Business'}]
            },
            'businesses': {},
            'performance': {}
        }
        
        statistics_panel.load_statistics(test_stats)
        
        # Check that items are not editable
        item = statistics_panel.most_used_table.item(0, 0)
        assert not (item.flags() & Qt.ItemFlag.ItemIsEditable)
    
    def test_summary_cards(self, statistics_panel):
        """Test that summary cards display correctly."""
        test_stats = {
            'keywords': {
                'total_businesses': 10,
                'total_keywords': 25,
                'total_usage': 150
            },
            'performance': {
                'keyword_efficiency': 80.0
            }
        }
        
        statistics_panel.load_statistics(test_stats)
        
        # Check that summary cards contain the expected values
        total_businesses_text = statistics_panel.total_businesses_label.text()
        assert '10' in total_businesses_text
        
        total_keywords_text = statistics_panel.total_keywords_label.text()
        assert '25' in total_keywords_text
        
        total_usage_text = statistics_panel.total_usage_label.text()
        assert '150' in total_usage_text
        
        efficiency_text = statistics_panel.efficiency_label.text()
        assert '80.0%' in efficiency_text


class TestStatisticsIntegration:
    """Integration tests for statistics functionality."""
    
    def test_full_statistics_workflow(self, qapp, qtbot):
        """Test the complete statistics workflow from database to GUI."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Setup database and managers
            db_manager = DatabaseManager(db_path)
            business_mapping_manager = BusinessMappingManager(db_manager)
            
            # Add test data
            business_mapping_manager.add_business("Integration Business 1")
            business_mapping_manager.add_business("Integration Business 2")
            
            business_mapping_manager.add_keyword("Integration Business 1", "int_keyword1", 0)
            business_mapping_manager.add_keyword("Integration Business 1", "int_keyword2", 1)
            business_mapping_manager.add_keyword("Integration Business 2", "int_keyword3", 0)
            
            # Simulate usage
            db_manager.execute_query(
                "UPDATE business_keywords SET usage_count = 15, last_used = '2024-01-16 10:00:00' WHERE keyword = 'int_keyword1'"
            )
            db_manager.execute_query(
                "UPDATE business_keywords SET usage_count = 8, last_used = '2024-01-15 10:00:00' WHERE keyword = 'int_keyword2'"
            )
            db_manager.execute_query(
                "UPDATE business_keywords SET usage_count = 22, last_used = '2024-01-17 10:00:00' WHERE keyword = 'int_keyword3'"
            )
            
            # Get comprehensive statistics
            stats = business_mapping_manager.get_comprehensive_statistics()
            
            # Create and populate statistics panel
            statistics_panel = StatisticsPanel()
            qtbot.addWidget(statistics_panel)
            statistics_panel.load_statistics(stats)
            
            # Verify the data flows correctly
            assert stats['keywords']['total_businesses'] == 2
            assert stats['keywords']['total_keywords'] == 5  # 3 manual + 2 automatic (one per business)
            assert stats['keywords']['total_usage'] == 45
            
            # Check that the panel displays the data
            assert statistics_panel.most_used_table.rowCount() == 3
            assert statistics_panel.most_used_table.item(0, 0).text() == 'int_keyword3'  # Highest usage
            
        finally:
            db_manager.close()
            os.unlink(db_path) 