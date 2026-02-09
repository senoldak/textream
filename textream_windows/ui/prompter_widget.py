from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPainter, QBrush, QTextCursor, QTextCharFormat, QFont, QPainterPath
from settings import settings

class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.levels = [0.0] * 30
        self.setFixedHeight(30)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def update_level(self, level):
        self.levels.append(level)
        if len(self.levels) > 30:
            self.levels.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        bar_count = len(self.levels)
        bar_width = width / bar_count
        
        color_base = QColor(settings.waveform_color)
        style = settings.waveform_style

        for i, level in enumerate(self.levels):
            h = max(4, level * height)
            x = i * bar_width
            y = (height - h) / 2
            
            alpha = int(100 + (level * 155))
            color = QColor(color_base.red(), color_base.green(), color_base.blue(), alpha)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)

            if style == "bars":
                painter.drawRoundedRect(int(x), int(y), int(bar_width - 2), int(h), 2, 2)
            elif style == "dots":
                dot_size = int(max(3, level * 10))
                painter.drawEllipse(int(x + bar_width/2 - dot_size/2), int(height/2 - dot_size/2), dot_size, dot_size)
            elif style == "wave":
                if i > 0:
                    prev_h = max(4, self.levels[i-1] * height)
                    prev_y = (height - prev_h) / 2
                    painter.setPen(color)
                    painter.drawLine(int(x - bar_width), int(prev_y + prev_h/2), int(x), int(y + h/2))
            elif style == "solid":
                # Filled area wave
                if i > 0:
                    prev_h = max(4, self.levels[i-1] * height)
                    path = QPainterPath()
                    path.moveTo(x - bar_width, height)
                    path.lineTo(x - bar_width, height - prev_h)
                    path.lineTo(x, height - h)
                    path.lineTo(x, height)
                    path.closeSubpath()
                    painter.fillPath(path, QBrush(color))
            elif style == "mirrored":
                # Bars expanding from center in both directions
                center_y = height / 2
                painter.drawRoundedRect(int(x), int(center_y - h/2), int(bar_width - 2), int(h), 1, 1)
            elif style == "outline":
                # Only borders
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(color)
                painter.drawRect(int(x), int(y), int(bar_width - 2), int(h))

class PrompterWidget(QWidget):
    jump_requested = pyqtSignal(int)      # Emits char offset
    pause_requested = pyqtSignal(bool)   # Emits True if paused
    rewind_requested = pyqtSignal()
    forward_requested = pyqtSignal()
    speed_changed = pyqtSignal(int)      # Emits speed level (0-5)
    speed_changed = pyqtSignal(int)      # Emits speed level (0-5)
    auto_advance_requested = pyqtSignal() # Emitted when timer ticks
    language_changed = pyqtSignal(str)   # Language switch
    mic_toggled = pyqtSignal(bool)       # Emits True if mic is ON (active)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 5)
        self.layout.setSpacing(5)

        # Text Area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFrameStyle(0)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setStyleSheet("background: transparent; color: white;")
        
        font = QFont(settings.font_family, settings.font_size)
        self.text_edit.setFont(font)
        self.layout.addWidget(self.text_edit)

        # Disable mouse interaction for text_edit so dragging the window is easier
        self.text_edit.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Controls Layout
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setContentsMargins(5, 0, 5, 0)
        self.controls_layout.setSpacing(8)

        btn_style = """
            QPushButton { 
                background-color: rgba(255, 255, 255, 15); 
                color: white; 
                border-radius: 12px; 
                border: none;
                font-size: 13px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 30); }
        """

        self.btn_rewind = QPushButton("↺")
        self.btn_rewind.setFixedSize(24, 24)
        self.btn_rewind.setStyleSheet(btn_style)
        self.btn_rewind.clicked.connect(self.rewind_requested.emit)
        
        self.btn_play_pause = QPushButton("⏸")
        self.btn_play_pause.setFixedSize(24, 24)
        self.btn_play_pause.setStyleSheet(btn_style)
        self.is_paused = False
        self.btn_play_pause.clicked.connect(self._toggle_pause)

        self.btn_speed = QPushButton("OFF")
        self.btn_speed.setFixedSize(36, 24)
        self.btn_speed.setStyleSheet(btn_style + "font-weight: bold; font-size: 9px;")
        self.speed_level = 0
        self.btn_speed.clicked.connect(self._cycle_speed)

        self.btn_forward = QPushButton("↻")
        self.btn_forward.setFixedSize(24, 24)
        self.btn_forward.setStyleSheet(btn_style)
        self.btn_forward.clicked.connect(self.forward_requested.emit)

        self.btn_mic = QPushButton("🎤")
        self.btn_mic.setFixedSize(24, 24)
        self.btn_mic.setStyleSheet(btn_style)
        self.is_mic_on = True
        self.btn_mic.clicked.connect(self._toggle_mic)

        self.controls_layout.addStretch()
        self.controls_layout.addWidget(self.btn_rewind)
        self.controls_layout.addWidget(self.btn_play_pause)
        self.controls_layout.addWidget(self.btn_mic)
        self.controls_layout.addWidget(self.btn_speed)
        self.controls_layout.addWidget(self.btn_forward)
        self.controls_layout.addStretch()

        self.layout.addLayout(self.controls_layout)

        # Bottom Waveform
        self.waveform = WaveformWidget()
        self.layout.addWidget(self.waveform)

        self.full_text = ""
        self.current_offset = 0
        
        # Auto-advance timer
        self.advance_timer = QTimer()
        self.advance_timer.timeout.connect(self._on_advance_tick)

    def _cycle_speed(self):
        self.speed_level = (self.speed_level + 1) % 6
        speeds = ["OFF", "1x", "2x", "3x", "4x", "5x"]
        self.btn_speed.setText(speeds[self.speed_level])
        
        if self.speed_level == 0:
            self.advance_timer.stop()
        else:
            interval = 300 - (self.speed_level * 50)
            self.advance_timer.start(interval)
        
        self.speed_changed.emit(self.speed_level)

    def _on_advance_tick(self):
        if not self.is_paused:
            self.auto_advance_requested.emit()

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        self.btn_play_pause.setText("▶" if self.is_paused else "⏸")
        self.pause_requested.emit(self.is_paused)

    def _toggle_mic(self):
        self.is_mic_on = not self.is_mic_on
        self.btn_mic.setText("🎤" if self.is_mic_on else "🔇")
        self.mic_toggled.emit(self.is_mic_on)

    def set_text(self, text):
        self.full_text = text
        self.current_offset = 0
        self.update_display()
        self.adjust_height()

    def adjust_height(self):
        # Calculate height based on line_count setting
        line_height = self.text_edit.fontMetrics().lineSpacing()
        total_text_height = line_height * settings.line_count
        self.text_edit.setFixedHeight(total_text_height + 20)

    def update_progress(self, char_count):
        self.current_offset = char_count
        self.update_display()
        self.auto_scroll()

    def update_audio_level(self, level):
        self.waveform.update_level(level)

    def update_display(self):
        cursor = self.text_edit.textCursor()
        scroll_val = self.text_edit.verticalScrollBar().value()
        
        if self.text_edit.toPlainText() != self.full_text:
             self.text_edit.setText(self.full_text)

        # Theme-aware styles for controls
        is_dark = settings.theme == "dark"
        btn_fg = "white" if is_dark else "#333333"
        btn_bg_alpha = "15" if is_dark else "25"
        btn_hover_alpha = "30" if is_dark else "40"
        
        btn_style = f"""
            QPushButton {{ 
                background-color: rgba({"255, 255, 255" if is_dark else "0, 0, 0"}, {btn_bg_alpha}); 
                color: {btn_fg}; 
                border-radius: 12px; 
                border: none;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: rgba({"255, 255, 255" if is_dark else "0, 0, 0"}, {btn_hover_alpha}); }}
        """
        
        # Apply updated style to all buttons
        self.btn_rewind.setStyleSheet(btn_style)
        self.btn_play_pause.setStyleSheet(btn_style)
        self.btn_mic.setStyleSheet(btn_style)
        self.btn_forward.setStyleSheet(btn_style)
        self.btn_speed.setStyleSheet(btn_style + "font-weight: bold; font-size: 9px;")

        # Base Style
        current_font = QFont(settings.font_family, settings.font_size)
        self.text_edit.setFont(current_font)

        # Base Color (Dimmed)
        base_color = QColor(settings.text_color)
        base_color.setAlpha(80) # 80/255 opacity
        
        cursor.select(QTextCursor.SelectionType.Document)
        format_dim = QTextCharFormat()
        format_dim.setFont(current_font)
        format_dim.setForeground(base_color)
        cursor.setCharFormat(format_dim)
        
        if self.current_offset > 0:
            cursor.setPosition(0)
            cursor.setPosition(min(self.current_offset, len(self.full_text)), QTextCursor.MoveMode.KeepAnchor)
            format_highlight = QTextCharFormat()
            format_highlight.setFont(current_font)
            format_highlight.setForeground(QColor(settings.highlight_color))
            cursor.setCharFormat(format_highlight)
        
        self.text_edit.verticalScrollBar().setValue(scroll_val)

    def auto_scroll(self):
        cursor = self.text_edit.textCursor()
        cursor.setPosition(self.current_offset)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()
