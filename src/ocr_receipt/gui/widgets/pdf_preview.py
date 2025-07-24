from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QPixmap, QImage
from pdf2image import convert_from_path
import os
from PIL.ImageQt import ImageQt

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
        self._pdf_path = None
        self._page_images = []  # List of PIL Images
        self._fit_width_mode = False
        self._fit_height_mode = False
        # Panning state
        self._panning = False
        self._pan_start = None
        self._pan_offset = [0, 0]
        self._pixmap_size = (0, 0)

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
        self.fit_width_btn = QPushButton("Fit Width")
        self.fit_height_btn = QPushButton("Fit Height")
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.page_label)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Zoom:"))
        controls_layout.addWidget(self.zoom_out_btn)
        controls_layout.addWidget(self.zoom_slider)
        controls_layout.addWidget(self.zoom_in_btn)
        controls_layout.addWidget(self.fit_width_btn)
        controls_layout.addWidget(self.fit_height_btn)
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
        # Install event filter for mouse wheel zoom
        self.pdf_label.installEventFilter(self)
        # Enable mouse tracking for panning
        self.pdf_label.setMouseTracking(True)

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
        self.fit_width_btn.clicked.connect(self._on_fit_width)
        self.fit_height_btn.clicked.connect(self._on_fit_height)

    def _on_fit_height(self) -> None:
        self._fit_height_mode = True
        self._fit_width_mode = False
        self._update_view()

    def _on_fit_width(self) -> None:
        self._fit_width_mode = True
        self._fit_height_mode = False
        self._update_view()

    def load_pdf(self, pdf_path: str) -> None:
        """
        Load the PDF and display the first page.
        """
        self._pdf_path = pdf_path
        self.current_page = 1
        self._page_images = []
        if not os.path.exists(pdf_path):
            self.total_pages = 1
            self.pdf_label.setText("[File not found]")
            return
        try:
            # Convert all pages to PIL images
            self._page_images = convert_from_path(pdf_path)
            self.total_pages = len(self._page_images)
        except Exception as e:
            self.total_pages = 1
            self.pdf_label.setText(f"[PDF Load Error: {e}]")
            return
        self._update_view()

    def _update_view(self) -> None:
        self.page_label.setText(f"Page {self.current_page}/{self.total_pages}")
        if not self._page_images or self.current_page < 1 or self.current_page > self.total_pages:
            self.pdf_label.setText("[No PDF Loaded]")
            return
        pil_image = self._page_images[self.current_page - 1]
        w, h = pil_image.size
        if self._fit_width_mode:
            label_width = self.pdf_label.width()
            if label_width < 10:
                label_width = 400  # fallback
            scale = label_width / w
            new_w, new_h = int(w * scale), int(h * scale)
        elif self._fit_height_mode:
            label_height = self.pdf_label.height()
            if label_height < 10:
                label_height = 600  # fallback
            scale = label_height / h
            new_w, new_h = int(w * scale), int(h * scale)
        else:
            scale = self.zoom_level / 100.0
            new_w, new_h = int(w * scale), int(h * scale)
        pil_image_resized = pil_image.resize((new_w, new_h))
        qt_image = ImageQt(pil_image_resized.convert("RGBA"))
        pixmap = QPixmap.fromImage(qt_image)
        self._pixmap_size = (new_w, new_h)
        # Only allow panning if image is larger than label
        label_w, label_h = self.pdf_label.width(), self.pdf_label.height()
        max_offset_x = max(0, new_w - label_w)
        max_offset_y = max(0, new_h - label_h)
        # Clamp pan offset
        self._pan_offset[0] = min(max(self._pan_offset[0], -max_offset_x), 0)
        self._pan_offset[1] = min(max(self._pan_offset[1], -max_offset_y), 0)
        # Draw the visible part of the pixmap
        if new_w > label_w or new_h > label_h:
            visible_pixmap = pixmap.copy(-self._pan_offset[0], -self._pan_offset[1], label_w, label_h)
            self.pdf_label.setPixmap(visible_pixmap)
        else:
            self._pan_offset = [0, 0]
            self.pdf_label.setPixmap(pixmap)
        if self._fit_width_mode:
            self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        elif self._fit_height_mode:
            self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        else:
            self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Reset pan if zoom or page changes
        if not self._panning:
            self._pan_offset = [0, 0]

    def _on_prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self._update_view()

    def _on_next_page(self) -> None:
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._update_view()

    def _on_zoom_out(self) -> None:
        self._fit_width_mode = False
        self._fit_height_mode = False
        self.zoom_level = max(10, self.zoom_level - 10)
        self.zoom_slider.setValue(self.zoom_level)
        self._update_view()

    def _on_zoom_in(self) -> None:
        self._fit_width_mode = False
        self._fit_height_mode = False
        self.zoom_level = min(300, self.zoom_level + 10)
        self.zoom_slider.setValue(self.zoom_level)
        self._update_view()

    def _on_zoom_slider(self, value: int) -> None:
        self._fit_width_mode = False
        self._fit_height_mode = False
        self.zoom_level = value
        self._update_view()

    def eventFilter(self, obj, event):
        if obj == self.pdf_label and event.type() == QEvent.Type.Wheel:
            self._fit_width_mode = False
            self._fit_height_mode = False
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_level = min(300, self.zoom_level + 10)
            else:
                self.zoom_level = max(10, self.zoom_level - 10)
            self.zoom_slider.setValue(self.zoom_level)
            self._update_view()
            return True
        # Mouse press for panning
        if obj == self.pdf_label and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self._panning = True
                self._pan_start = event.position().toPoint()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                return True
        # Mouse move for panning
        if obj == self.pdf_label and event.type() == QEvent.Type.MouseMove:
            if self._panning and self._pixmap_size != (0, 0):
                delta = event.position().toPoint() - self._pan_start
                self._pan_start = event.position().toPoint()
                self._pan_offset[0] += delta.x()
                self._pan_offset[1] += delta.y()
                self._update_view()
                return True
        # Mouse release for panning
        if obj == self.pdf_label and event.type() == QEvent.Type.MouseButtonRelease:
            if event.button() == Qt.MouseButton.LeftButton:
                self._panning = False
                self.setCursor(Qt.CursorShape.ArrowCursor)
                return True
        return super().eventFilter(obj, event) 