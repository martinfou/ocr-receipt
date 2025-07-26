"""
Statistics Panel Widget for OCR Receipt Parser.

Displays comprehensive statistics and reporting data for business keywords.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QGroupBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QPushButton, QTabWidget, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from typing import Dict, Any, List

class StatisticsPanel(QWidget):
    """
    Comprehensive statistics panel for displaying keyword and business statistics.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different statistic categories
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_overview_tab()
        self._create_keyword_stats_tab()
        self._create_business_stats_tab()
        self._create_performance_tab()
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        self.refresh_button = QPushButton("Refresh Statistics")
        self.refresh_button.clicked.connect(self.refresh_statistics)
        refresh_layout.addWidget(self.refresh_button)
        layout.addLayout(refresh_layout)
        
    def _create_overview_tab(self):
        """Create the overview tab with summary statistics."""
        overview_widget = QWidget()
        layout = QVBoxLayout(overview_widget)
        
        # Summary cards
        summary_layout = QGridLayout()
        
        # Create summary cards
        self.total_businesses_label = self._create_summary_card("Total Businesses", "0")
        self.total_keywords_label = self._create_summary_card("Total Keywords", "0")
        self.total_usage_label = self._create_summary_card("Total Usage", "0")
        self.efficiency_label = self._create_summary_card("Keyword Efficiency", "0%")
        
        # Add cards to grid
        summary_layout.addWidget(self.total_businesses_label, 0, 0)
        summary_layout.addWidget(self.total_keywords_label, 0, 1)
        summary_layout.addWidget(self.total_usage_label, 1, 0)
        summary_layout.addWidget(self.efficiency_label, 1, 1)
        
        layout.addLayout(summary_layout)
        
        # Quick stats
        quick_stats_group = QGroupBox("Quick Statistics")
        quick_stats_layout = QVBoxLayout(quick_stats_group)
        
        self.quick_stats_label = QLabel()
        self.quick_stats_label.setWordWrap(True)
        quick_stats_layout.addWidget(self.quick_stats_label)
        
        layout.addWidget(quick_stats_group)
        layout.addStretch()
        
        self.tab_widget.addTab(overview_widget, "Overview")
        
    def _create_keyword_stats_tab(self):
        """Create the keyword statistics tab."""
        keyword_widget = QWidget()
        layout = QVBoxLayout(keyword_widget)
        
        # Most used keywords table
        most_used_group = QGroupBox("Most Used Keywords")
        most_used_layout = QVBoxLayout(most_used_group)
        
        self.most_used_table = QTableWidget()
        self.most_used_table.setColumnCount(3)
        self.most_used_table.setHorizontalHeaderLabels(["Keyword", "Usage Count", "Business"])
        self.most_used_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        most_used_layout.addWidget(self.most_used_table)
        
        layout.addWidget(most_used_group)
        
        # Recently used keywords table
        recent_group = QGroupBox("Recently Used Keywords")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(3)
        self.recent_table.setHorizontalHeaderLabels(["Keyword", "Last Used", "Business"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        recent_layout.addWidget(self.recent_table)
        
        layout.addWidget(recent_group)
        
        # Usage distribution
        usage_group = QGroupBox("Usage Distribution")
        usage_layout = QVBoxLayout(usage_group)
        
        self.usage_table = QTableWidget()
        self.usage_table.setColumnCount(2)
        self.usage_table.setHorizontalHeaderLabels(["Usage Range", "Count"])
        self.usage_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        usage_layout.addWidget(self.usage_table)
        
        layout.addWidget(usage_group)
        
        self.tab_widget.addTab(keyword_widget, "Keyword Statistics")
        
    def _create_business_stats_tab(self):
        """Create the business statistics tab."""
        business_widget = QWidget()
        layout = QVBoxLayout(business_widget)
        
        # Business by total usage
        usage_group = QGroupBox("Businesses by Total Usage")
        usage_layout = QVBoxLayout(usage_group)
        
        self.business_usage_table = QTableWidget()
        self.business_usage_table.setColumnCount(2)
        self.business_usage_table.setHorizontalHeaderLabels(["Business", "Total Usage"])
        self.business_usage_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        usage_layout.addWidget(self.business_usage_table)
        
        layout.addWidget(usage_group)
        
        # Business by keyword count
        keyword_count_group = QGroupBox("Businesses by Keyword Count")
        keyword_count_layout = QVBoxLayout(keyword_count_group)
        
        self.business_keyword_count_table = QTableWidget()
        self.business_keyword_count_table.setColumnCount(2)
        self.business_keyword_count_table.setHorizontalHeaderLabels(["Business", "Keyword Count"])
        self.business_keyword_count_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        keyword_count_layout.addWidget(self.business_keyword_count_table)
        
        layout.addWidget(keyword_count_group)
        
        # Business by average usage
        avg_usage_group = QGroupBox("Businesses by Average Usage per Keyword")
        avg_usage_layout = QVBoxLayout(avg_usage_group)
        
        self.business_avg_usage_table = QTableWidget()
        self.business_avg_usage_table.setColumnCount(3)
        self.business_avg_usage_table.setHorizontalHeaderLabels(["Business", "Keyword Count", "Avg Usage"])
        self.business_avg_usage_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        avg_usage_layout.addWidget(self.business_avg_usage_table)
        
        layout.addWidget(avg_usage_group)
        
        self.tab_widget.addTab(business_widget, "Business Statistics")
        
    def _create_performance_tab(self):
        """Create the performance metrics tab."""
        performance_widget = QWidget()
        layout = QVBoxLayout(performance_widget)
        
        # Performance metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        self.efficiency_metric_label = self._create_metric_label("Keyword Efficiency", "0%")
        self.avg_keywords_label = self._create_metric_label("Avg Keywords per Business", "0")
        self.case_sensitive_label = self._create_metric_label("Case Sensitive Keywords", "0")
        self.case_insensitive_label = self._create_metric_label("Case Insensitive Keywords", "0")
        
        metrics_layout.addWidget(self.efficiency_metric_label, 0, 0)
        metrics_layout.addWidget(self.avg_keywords_label, 0, 1)
        metrics_layout.addWidget(self.case_sensitive_label, 1, 0)
        metrics_layout.addWidget(self.case_insensitive_label, 1, 1)
        
        layout.addWidget(metrics_group)
        
        # Most efficient keywords
        efficient_group = QGroupBox("Most Efficient Keywords")
        efficient_layout = QVBoxLayout(efficient_group)
        
        self.efficient_table = QTableWidget()
        self.efficient_table.setColumnCount(3)
        self.efficient_table.setHorizontalHeaderLabels(["Keyword", "Usage Count", "Business"])
        self.efficient_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        efficient_layout.addWidget(self.efficient_table)
        
        layout.addWidget(efficient_group)
        
        # Unused keywords
        unused_group = QGroupBox("Unused Keywords")
        unused_layout = QVBoxLayout(unused_group)
        
        self.unused_table = QTableWidget()
        self.unused_table.setColumnCount(2)
        self.unused_table.setHorizontalHeaderLabels(["Keyword", "Business"])
        self.unused_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        unused_layout.addWidget(self.unused_table)
        
        layout.addWidget(unused_group)
        
        self.tab_widget.addTab(performance_widget, "Performance")
        
    def _create_summary_card(self, title: str, value: str) -> QLabel:
        """Create a summary card widget."""
        card = QLabel()
        card.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
        """)
        card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.setMinimumHeight(80)
        
        # Create rich text for the card
        card_text = f"""
        <div style='text-align: center;'>
            <div style='font-size: 14px; color: #666; margin-bottom: 5px;'>{title}</div>
            <div style='font-size: 24px; font-weight: bold; color: #333;'>{value}</div>
        </div>
        """
        card.setText(card_text)
        
        return card
        
    def _create_metric_label(self, title: str, value: str) -> QLabel:
        """Create a metric label widget."""
        label = QLabel()
        label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 8px;
                margin: 2px;
            }
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumHeight(60)
        
        label_text = f"""
        <div style='text-align: center;'>
            <div style='font-size: 12px; color: #666;'>{title}</div>
            <div style='font-size: 18px; font-weight: bold; color: #333;'>{value}</div>
        </div>
        """
        label.setText(label_text)
        
        return label
        
    def _populate_table(self, table: QTableWidget, data: List[Dict[str, Any]], columns: List[str]):
        """Populate a table with data."""
        table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            for col, column_name in enumerate(columns):
                value = item.get(column_name, "")
                if isinstance(value, (int, float)):
                    value = str(value)
                table_item = QTableWidgetItem(str(value))
                table_item.setFlags(table_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, col, table_item)
                
    def load_statistics(self, stats: Dict[str, Any]):
        """Load and display statistics data."""
        try:
            # Overview tab
            keyword_stats = stats.get('keywords', {})
            performance_stats = stats.get('performance', {})
            
            # Update summary cards
            self.total_businesses_label.setText(f"""
            <div style='text-align: center;'>
                <div style='font-size: 14px; color: #666; margin-bottom: 5px;'>Total Businesses</div>
                <div style='font-size: 24px; font-weight: bold; color: #333;'>{keyword_stats.get('total_businesses', 0)}</div>
            </div>
            """)
            
            self.total_keywords_label.setText(f"""
            <div style='text-align: center;'>
                <div style='font-size: 14px; color: #666; margin-bottom: 5px;'>Total Keywords</div>
                <div style='font-size: 24px; font-weight: bold; color: #333;'>{keyword_stats.get('total_keywords', 0)}</div>
            </div>
            """)
            
            self.total_usage_label.setText(f"""
            <div style='text-align: center;'>
                <div style='font-size: 14px; color: #666; margin-bottom: 5px;'>Total Usage</div>
                <div style='font-size: 24px; font-weight: bold; color: #333;'>{keyword_stats.get('total_usage', 0)}</div>
            </div>
            """)
            
            self.efficiency_label.setText(f"""
            <div style='text-align: center;'>
                <div style='font-size: 14px; color: #666; margin-bottom: 5px;'>Keyword Efficiency</div>
                <div style='font-size: 24px; font-weight: bold; color: #333;'>{performance_stats.get('keyword_efficiency', 0)}%</div>
            </div>
            """)
            
            # Quick stats
            quick_stats_text = f"""
            <b>Case Sensitivity:</b> {keyword_stats.get('case_sensitive_keywords', 0)} case-sensitive, 
            {keyword_stats.get('case_insensitive_keywords', 0)} case-insensitive<br>
            <b>Average Usage:</b> {keyword_stats.get('average_usage', 0)} per keyword<br>
            <b>Maximum Usage:</b> {keyword_stats.get('max_usage', 0)} by a single keyword<br>
            <b>Average Keywords per Business:</b> {performance_stats.get('avg_keywords_per_business', 0)}
            """
            self.quick_stats_label.setText(quick_stats_text)
            
            # Keyword statistics tab
            self._populate_table(
                self.most_used_table,
                keyword_stats.get('most_used_keywords', []),
                ['keyword', 'usage_count', 'business_name']
            )
            
            self._populate_table(
                self.recent_table,
                keyword_stats.get('recently_used_keywords', []),
                ['keyword', 'last_used', 'business_name']
            )
            
            self._populate_table(
                self.usage_table,
                keyword_stats.get('keywords_by_usage_range', []),
                ['usage_range', 'count']
            )
            
            # Business statistics tab
            business_stats = stats.get('businesses', {})
            
            self._populate_table(
                self.business_usage_table,
                business_stats.get('businesses_by_total_usage', []),
                ['business_name', 'total_usage']
            )
            
            self._populate_table(
                self.business_keyword_count_table,
                keyword_stats.get('businesses_by_keyword_count', []),
                ['business_name', 'keyword_count']
            )
            
            self._populate_table(
                self.business_avg_usage_table,
                business_stats.get('businesses_by_avg_usage', []),
                ['business_name', 'keyword_count', 'avg_usage_per_keyword']
            )
            
            # Performance tab
            self.efficiency_metric_label.setText(f"""
            <div style='text-align: center;'>
                <div style='font-size: 12px; color: #666;'>Keyword Efficiency</div>
                <div style='font-size: 18px; font-weight: bold; color: #333;'>{performance_stats.get('keyword_efficiency', 0)}%</div>
            </div>
            """)
            
            self.avg_keywords_label.setText(f"""
            <div style='text-align: center;'>
                <div style='font-size: 12px; color: #666;'>Avg Keywords per Business</div>
                <div style='font-size: 18px; font-weight: bold; color: #333;'>{performance_stats.get('avg_keywords_per_business', 0)}</div>
            </div>
            """)
            
            self.case_sensitive_label.setText(f"""
            <div style='text-align: center;'>
                <div style='font-size: 12px; color: #666;'>Case Sensitive Keywords</div>
                <div style='font-size: 18px; font-weight: bold; color: #333;'>{keyword_stats.get('case_sensitive_keywords', 0)}</div>
            </div>
            """)
            
            self.case_insensitive_label.setText(f"""
            <div style='text-align: center;'>
                <div style='font-size: 12px; color: #666;'>Case Insensitive Keywords</div>
                <div style='font-size: 18px; font-weight: bold; color: #333;'>{keyword_stats.get('case_insensitive_keywords', 0)}</div>
            </div>
            """)
            
            self._populate_table(
                self.efficient_table,
                performance_stats.get('most_efficient_keywords', []),
                ['keyword', 'usage_count', 'business_name']
            )
            
            self._populate_table(
                self.unused_table,
                keyword_stats.get('unused_keywords', []),
                ['keyword', 'business_name']
            )
            
        except Exception as e:
            print(f"Error loading statistics: {e}")
            
    def refresh_statistics(self):
        """Emit signal to refresh statistics."""
        # This will be connected to the parent widget's refresh method
        pass 