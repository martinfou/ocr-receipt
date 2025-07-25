from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget
from PyQt6.QtCore import Qt
from typing import List, Dict, Any

class KeywordsTable(QTableWidget):
    """
    Table widget for displaying business keywords and their properties.
    """
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            "Business",
            "Keyword",
            "Case Sensitive",
            "Usage Count",
            "Last Used"
        ])
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.setSortingEnabled(True)

    def load_keywords(self, keywords: List[Dict[str, Any]]) -> None:
        """
        Load a list of keyword dictionaries into the table.
        """
        self.setRowCount(0)
        for keyword in keywords:
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(str(keyword.get("business_name", ""))))
            self.setItem(row, 1, QTableWidgetItem(str(keyword.get("keyword", ""))))
            self.setItem(row, 2, QTableWidgetItem("Yes" if keyword.get("is_case_sensitive", False) else "No"))
            self.setItem(row, 3, QTableWidgetItem(str(keyword.get("usage_count", 0))))
            self.setItem(row, 4, QTableWidgetItem(str(keyword.get("last_used", ""))))
        self.resizeColumnsToContents() 