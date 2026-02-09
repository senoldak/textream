from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox, QPushButton, QColorDialog
from PyQt6.QtCore import Qt
from settings import settings

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayarlar")
        self.setFixedSize(300, 350)
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)

        # Line Count
        line_layout = QHBoxLayout()
        line_layout.addWidget(QLabel("Satır Sayısı:"))
        self.line_spin = QSpinBox()
        self.line_spin.setRange(1, 10)
        self.line_spin.setValue(settings.line_count)
        line_layout.addWidget(self.line_spin)
        self.layout.addLayout(line_layout)

        # Waveform Style
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Dalga Şekli:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Çubuklar (Bars)", "Noktalar (Dots)", "Dalga (Wave)"])
        # Map values
        style_map = {"bars": 0, "dots": 1, "wave": 2}
        self.style_combo.setCurrentIndex(style_map.get(settings.waveform_style, 0))
        style_layout.addWidget(self.style_combo)
        self.layout.addLayout(style_layout)

        # Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Dalga Rengi:"))
        self.btn_color = QPushButton()
        self.btn_color.setFixedSize(50, 25)
        self._set_color_btn(settings.waveform_color)
        self.btn_color.clicked.connect(self._pick_color)
        color_layout.addWidget(self.btn_color)
        self.layout.addLayout(color_layout)
        self.current_color = settings.waveform_color

        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Tema:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Koyu (Dark)", "Açık (Light)"])
        self.theme_combo.setCurrentIndex(0 if settings.theme == "dark" else 1)
        theme_layout.addWidget(self.theme_combo)
        self.layout.addLayout(theme_layout)

        # Save
        self.btn_save = QPushButton("Kaydet")
        self.btn_save.clicked.connect(self.save)
        self.layout.addWidget(self.btn_save)

    def _set_color_btn(self, color):
        self.btn_color.setStyleSheet(f"background-color: {color}; border: 1px solid white;")

    def _pick_color(self):
        color = QColorDialog.getColor(Qt.GlobalColor.yellow, self, "Renk Seç")
        if color.isValid():
            self.current_color = color.name()
            self._set_color_btn(self.current_color)

    def save(self):
        settings.line_count = self.line_spin.value()
        
        style_map = {0: "bars", 1: "dots", 2: "wave"}
        settings.waveform_style = style_map[self.style_combo.currentIndex()]
        settings.waveform_color = self.current_color
        settings.theme = "dark" if self.theme_combo.currentIndex() == 0 else "light"
        
        self.accept()
