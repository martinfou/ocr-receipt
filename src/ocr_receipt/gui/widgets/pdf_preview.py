from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class PDFPreview(QWidget):
    """
    Widget for displaying PDF pages with zoom and navigation controls.
    Now provides get_controls_widget() for external layout alignment.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_connections()
        self.current_page = 1
        self.total_pages = 1
        self.zoom_level = 100

    def _setup_ui(self) -> None:
        self._controls_widget = QWidget()
        controls_layout = QHBoxLayout(self._controls_widget)
        self.prev_btn = QPushButton("← Previous")
        self.page_label = QLabel("Page 1/1")
        self.next_btn = QPushButton("Next →")
        self.zoom_out_btn = QPushButton("-")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 300)
        self.zoom_slider.setValue(100)
        self.zoom_in_btn = QPushButton("+")
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.page_label)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Zoom:"))
        controls_layout.addWidget(self.zoom_out_btn)
        controls_layout.addWidget(self.zoom_slider)
        controls_layout.addWidget(self.zoom_in_btn)
        # PDF display area
        self.pdf_label = QLabel("[PDF Page Preview]")
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_label.setMinimumSize(400, 600)
        self.pdf_label.setStyleSheet("border: 1px solid #ccc; background: white;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._controls_widget)
        layout.addWidget(self.pdf_label)

    def get_controls_widget(self) -> QWidget:
        """
        Return the navigation/zoom controls widget for external layout.
        """
        return self._controls_widget

    def _setup_connections(self) -> None:
        self.prev_btn.clicked.connect(self._on_prev_page)
        self.next_btn.clicked.connect(self._on_next_page)
        self.zoom_out_btn.clicked.connect(self._on_zoom_out)
        self.zoom_in_btn.clicked.connect(self._on_zoom_in)
        self.zoom_slider.valueChanged.connect(self._on_zoom_slider)

    def load_pdf(self, pdf_path: str) -> None:
        """
        Load the PDF and display the first page. (Stub)
        """
        self.current_page = 1
        self.total_pages = 1  # TODO: Set actual page count
        self._update_view()

    def _update_view(self) -> None:
        self.page_label.setText(f"Page {self.current_page}/{self.total_pages}")
        # TODO: Render and display the current page as a QPixmap
        self.pdf_label.setText(f"PDF Page {self.current_page} (Zoom: {self.zoom_level}%)")

    def _on_prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self._update_view()

    def _on_next_page(self) -> None:
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._update_view()

    def _on_zoom_out(self) -> None:
        self.zoom_level = max(10, self.zoom_level - 10)
        self.zoom_slider.setValue(self.zoom_level)
        self._update_view()

    def _on_zoom_in(self) -> None:
        self.zoom_level = min(300, self.zoom_level + 10)
        self.zoom_slider.setValue(self.zoom_level)
        self._update_view()

    def _on_zoom_slider(self, value: int) -> None:
        self.zoom_level = value
        self._update_view() 