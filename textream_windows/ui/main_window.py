from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QHBoxLayout, QComboBox, QFrame, QScrollArea, QGridLayout, QColorDialog, QFontDialog, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QLinearGradient, QPalette, QBrush
from settings import settings

class MainWindow(QMainWindow):
    start_requested = pyqtSignal(str, str) # Emits (script text, lang_code)

    from locales import TRANSLATIONS
    TRANSLATIONS = TRANSLATIONS

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Textream - Modern Teleprompter")
        self.resize(900, 650) # Increased size
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Left Panel (Editor)
        self.editor_panel = QFrame()
        self.editor_layout = QVBoxLayout(self.editor_panel)
        self.editor_layout.setContentsMargins(40, 40, 40, 40)
        self.editor_layout.setSpacing(20)
        
        self.title_label = QLabel("Textream")
        self.title_label.setStyleSheet("font-size: 32px; font-weight: 800; color: #ffffff; letter-spacing: -1px;")
        self.editor_layout.addWidget(self.title_label)

        # Editor Container (for floating paste button)
        self.editor_container = QWidget()
        self.editor_cont_layout = QGridLayout(self.editor_container) # Grid for overlay
        self.editor_cont_layout.setContentsMargins(0,0,0,0)
        
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Senaryonuzu buraya yapıştırın...")
        self.text_editor.setFont(QFont("Inter", 13))
        self.text_editor.textChanged.connect(self._handle_text_edit)
        self.editor_cont_layout.addWidget(self.text_editor, 0, 0)

        # Floating Paste Button
        self.btn_paste = QPushButton("📋", self.editor_container)
        self.btn_paste.setFixedSize(36, 36)
        self.btn_paste.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: rgba(120, 120, 120, 100);
                border: none;
                border-radius: 8px;
                font-size: 18px;
            }
            QPushButton:hover { 
                background-color: rgba(120, 120, 120, 30); 
                color: #00a2ff;
            }
        """)
        self.btn_paste.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_paste.clicked.connect(self._on_paste)
        
        # Overlay positioning in grid
        self.editor_cont_layout.addWidget(self.btn_paste, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.btn_paste.setContentsMargins(0, 10, 10, 0) # Top and right margin
        
        self.editor_layout.addWidget(self.editor_container)
        self.btn_start = QPushButton("Stüdyoyu Başlat")
        self.btn_start.setObjectName("startBtn")
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self._on_start)
        self.editor_layout.addWidget(self.btn_start)
        
        self.main_layout.addWidget(self.editor_panel, stretch=3)

        # 2. Right Panel (Settings)
        self.settings_panel = QFrame()
        self.settings_panel.setFixedWidth(280) # Fixed width for a more compact and tidy look
        self.settings_panel.setStyleSheet("background-color: #0a0a0a; border-left: 1px solid #1a1a1a;")
        self.settings_layout = QVBoxLayout(self.settings_panel)
        self.settings_layout.setContentsMargins(20, 20, 20, 20)
        self.settings_layout.setSpacing(15)

        # Scroll area for settings if needed
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)

        # Language Segmented Group
        self.lbl_lang = QLabel("Diksiyon Dili:")
        scroll_layout.addWidget(self.lbl_lang)
        self.lang_group = QWidget()
        self.lang_layout = QGridLayout(self.lang_group) # Use grid for many languages
        self.lang_layout.setContentsMargins(0, 0, 0, 0)
        self.lang_layout.setSpacing(5)
        scroll_layout.addWidget(self.lang_group)

        # Theme Segmented Group
        self.lbl_theme = QLabel("Görünüm Teması:")
        scroll_layout.addWidget(self.lbl_theme)
        self.theme_group = QWidget()
        self.theme_layout = QHBoxLayout(self.theme_group)
        self.theme_layout.setContentsMargins(0, 0, 0, 0)
        self.theme_layout.setSpacing(5)
        scroll_layout.addWidget(self.theme_group)

        # Waveform Style Segmented Group
        self.lbl_wave = QLabel("Dalga Formu:")
        scroll_layout.addWidget(self.lbl_wave)
        self.wave_group = QWidget()
        self.wave_layout = QGridLayout(self.wave_group)
        self.wave_layout.setContentsMargins(0, 0, 0, 0)
        self.wave_layout.setSpacing(5)
        scroll_layout.addWidget(self.wave_group)

        # Colors Section
        scroll_layout.addSpacing(10)
        self.lbl_colors = QLabel("Renk Tercihleri:")
        scroll_layout.addWidget(self.lbl_colors)
        
        # Waveform Color
        self.lbl_wc = QLabel("Dalga Rengi:")
        scroll_layout.addWidget(self.lbl_wc)
        self.wc_group = QWidget()
        self.wc_layout = QGridLayout(self.wc_group)
        self.wc_layout.setContentsMargins(0, 0, 0, 0)
        self.wc_layout.setSpacing(5)
        scroll_layout.addWidget(self.wc_group)

        # Text Color
        self.lbl_tc = QLabel("Metin Rengi (Donuk):")
        scroll_layout.addWidget(self.lbl_tc)
        self.tc_group = QWidget()
        self.tc_layout = QGridLayout(self.tc_group)
        self.tc_layout.setContentsMargins(0, 0, 0, 0)
        self.tc_layout.setSpacing(5)
        scroll_layout.addWidget(self.tc_group)

        # Highlight Color
        self.lbl_hc = QLabel("Parlama Rengi:")
        scroll_layout.addWidget(self.lbl_hc)
        self.hc_group = QWidget()
        self.hc_layout = QGridLayout(self.hc_group)
        self.hc_layout.setContentsMargins(0, 0, 0, 0)
        self.hc_layout.setSpacing(5)
        scroll_layout.addWidget(self.hc_group)

        # Font Selection
        scroll_layout.addSpacing(10)
        self.lbl_font = QLabel("Yazı Tipi & Boyut:")
        scroll_layout.addWidget(self.lbl_font)
        
        self.font_btn_layout = QHBoxLayout()
        self.btn_font_pick = QPushButton("Font Seç...")
        self.btn_font_pick.clicked.connect(self._pick_font)
        self.btn_font_pick.setStyleSheet("""
            QPushButton {
                background-color: #222;
                color: #00a2ff;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2a2a2a; border: 1px solid #00a2ff; }
        """)
        self.font_btn_layout.addWidget(self.btn_font_pick)
        
        self.lbl_font_current = QLabel(f"{settings.font_family}, {settings.font_size}pt")
        self.lbl_font_current.setStyleSheet("font-size: 11px; color: #888; margin-top: 0px;")
        scroll_layout.addLayout(self.font_btn_layout)
        scroll_layout.addWidget(self.lbl_font_current)

        # Reset Settings Button
        scroll_layout.addSpacing(20)
        self.btn_reset = QPushButton("Varsayılanlara Dön")
        self.btn_reset.setObjectName("resetBtn")
        self.btn_reset.clicked.connect(self._reset_settings)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: rgba(255, 0, 0, 20); color: #ff4b4b; border: 1px solid #ff4b4b; }
        """)
        scroll_layout.addWidget(self.btn_reset)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)

        self.settings_layout.addWidget(scroll)
        
        self.main_layout.addWidget(self.settings_panel, stretch=1)

        # Background Gradient & Styles
        self._current_lang_code = "tr"
        self._is_sample_active = True
        self.apply_premium_styles()
        self._on_lang_changed("tr") # First run, also loads sample text

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Button is now handled by QGridLayout alignment, no manual move needed
        if hasattr(self, 'btn_paste'):
            self.btn_paste.raise_()


    def _pick_font(self):
        current_font = QFont(settings.font_family, settings.font_size)
        font, ok = QFontDialog.getFont(current_font, self) # Fixed: Font first then Bool
        if ok:
            settings.font_family = font.family()
            settings.font_size = font.pointSize()
            self.lbl_font_current.setText(f"{settings.font_family}, {settings.font_size}pt")
            print(f"Font updated to: {settings.font_family}, {settings.font_size}")

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()

    def create_segmented_group(self, layout, options, current_val, callback, is_grid=False, cols=3, show_picker=False, setting_key=None):
        self._clear_layout(layout)
        row, col = 0, 0
        
        is_dark = settings.theme == "dark"
        btn_bg = "#222" if is_dark else "#e8e8ed"
        btn_txt = "#888" if is_dark else "#6e6e73"
        btn_border = "#333" if is_dark else "#d2d2d7"
        btn_hover = "#2a2a2a" if is_dark else "#dadae0"
        
        # Helper for custom color selection
        def _pick_custom_color(k):
            color = QColorDialog.getColor()
            if color.isValid():
                hex_color = color.name().upper()
                self._update_setting(k, hex_color)
                self.retranslate_ui(self._current_lang_code) # Refresh everything

        for label, value in options.items():
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setChecked(value == current_val)
            
            # Custom Style for Segmented Buttons
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_bg};
                    color: {btn_txt};
                    border: 1px solid {btn_border};
                    border-radius: 6px;
                    padding: 6px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:checked {{
                    background-color: #0078d4;
                    color: white;
                    border: 1px solid #00a2ff;
                }}
                QPushButton:hover:!checked {{
                    background-color: {btn_hover};
                    color: {"#bbb" if is_dark else "#1d1d1f"};
                }}
            """)
            
            btn.clicked.connect(lambda checked, v=value: callback(v))
            
            if is_grid:
                layout.addWidget(btn, row, col)
                col += 1
                if col >= cols:
                    col = 0
                    row += 1
            else:
                layout.addWidget(btn)

        # Add '+' button for custom color if requested
        if show_picker and setting_key:
            picker_btn = QPushButton("+")
            picker_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {"#1a1a1a" if is_dark else "#ffffff"};
                    color: #00a2ff;
                    border: 1px dashed #00a2ff;
                    border-radius: 6px;
                    padding: 2px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #0078d4;
                    color: white;
                    border: 1px solid #00a2ff;
                }}
            """)
            picker_btn.setToolTip("Özel Renk Seç...")
            picker_btn.clicked.connect(lambda: _pick_custom_color(setting_key))
            
            if is_grid:
                layout.addWidget(picker_btn, row, col)
            else:
                layout.addWidget(picker_btn)

    def retranslate_ui(self, lang_code):
        t = self.TRANSLATIONS.get(lang_code, self.TRANSLATIONS["en"])
        
        self.setWindowTitle(t["title"])
        self.title_label.setText(t["editor_title"])
        self.text_editor.setPlaceholderText(t["placeholder"])
        self.btn_start.setText(t["start_btn"])
        
        self.lbl_lang.setText(t["lang_label"])
        self.lbl_theme.setText(t["theme_label"])
        self.lbl_wave.setText(t["wave_label"])
        self.lbl_colors.setText(t["colors_section"])
        
        self.lbl_wc.setText(t["wc_label"])
        self.lbl_tc.setText(t["tc_label"])
        self.lbl_hc.setText(t["hc_label"])
        
        self.lbl_font.setText(t["font_label"])
        self.btn_font_pick.setText(t["font_btn"])
        self.btn_reset.setText(t["reset_btn"])
        self.btn_paste.setToolTip(t["paste_tooltip"])

        # Update Language Selector (Segmented)
        self.create_segmented_group(
            self.lang_layout, 
            t["lang_names"], 
            lang_code, 
            self._on_lang_changed,
            is_grid=True, cols=2
        )

        # Theme (Segmented)
        themes = {"Dark": "dark", "Light": "light"} if lang_code == "en" else {"Koyu": "dark", "Açık": "light"}
        self.create_segmented_group(
            self.theme_layout,
            themes,
            settings.theme,
            lambda v: self._update_setting("theme", v)
        )

        # Wave Styles (Segmented)
        self.create_segmented_group(
            self.wave_layout,
            t["wave_styles"],
            settings.waveform_style,
            lambda v: self._update_setting("waveform_style", v),
            is_grid=True, cols=3
        )

        # Color presets (Segmented Grid)
        colors_map = t["color_presets"]
        self.create_segmented_group(self.wc_layout, colors_map, settings.waveform_color, lambda v: self._update_setting("waveform_color", v), is_grid=True, show_picker=True, setting_key="waveform_color")
        self.create_segmented_group(self.tc_layout, colors_map, settings.text_color, lambda v: self._update_setting("text_color", v), is_grid=True, show_picker=True, setting_key="text_color")
        self.create_segmented_group(self.hc_layout, colors_map, settings.highlight_color, lambda v: self._update_setting("highlight_color", v), is_grid=True, show_picker=True, setting_key="highlight_color")


    def _reset_settings(self):
        # Confirm with user? Usually for reset it's nice but user asked just to add it.
        # Let's just do it.
        settings.reset()
        print("Settings reset to defaults.")
        self.apply_premium_styles()
        self.retranslate_ui(self._current_lang_code)
        self.lbl_font_current.setText(f"{settings.font_family}, {settings.font_size}pt")

    def _update_setting(self, key, value):
        setattr(settings, key, value)
        print(f"Global setting updated: {key} = {value}")
        if key == "theme":
            self.apply_premium_styles()
            self.retranslate_ui(self._current_lang_code)

    def apply_premium_styles(self):
        is_dark = settings.theme == "dark"
        
        # Theme palette
        bg = "#0d0d0d" if is_dark else "#f5f5f7"
        central_bg = bg
        card_bg = "#121212" if is_dark else "#ffffff"
        text_primary = "#ffffff" if is_dark else "#1d1d1f"
        text_secondary = "#888888" if is_dark else "#6e6e73"
        border_clr = "#222222" if is_dark else "#d2d2d7"
        btn_bg = "#222" if is_dark else "#e8e8ed"
        btn_hover = "#2a2a2a" if is_dark else "#d2d2d7"
        settings_bg = "#0a0a0a" if is_dark else "#ffffff"

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {bg}; }}
            QWidget#centralWidget {{ background: {central_bg}; }}
            QLabel {{ color: {text_primary}; font-weight: 600; font-size: 11px; margin-top: 3px; }}
            QTextEdit {{
                background-color: {card_bg};
                color: {text_primary if not self._is_sample_active else "#555"};
                border: 1px solid {border_clr};
                border-radius: 10px;
                padding: 12px;
            }}
            QTextEdit:focus {{ border: 1px solid #0078d4; }}
            
            QPushButton#startBtn {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d4, stop:1 #00a2ff);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 15px;
                font-weight: 700;
            }}
            QPushButton#startBtn:hover {{ background: #106ebe; }}

            QPushButton {{ 
                background-color: {btn_bg}; 
                color: {text_secondary}; 
                border: 1px solid {border_clr}; 
                border-radius: 5px; 
                padding: 5px;
                font-size: 10px;
            }}
            QPushButton:hover {{ background-color: {btn_hover}; }}
            
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{
                border: none;
                background: {bg};
                width: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {text_secondary};
                min-height: 20px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {border_clr}; }}
        """)
        
        # Fixed styles for containers that should change
        if hasattr(self, 'settings_panel'):
            self.settings_panel.setStyleSheet(f"background-color: {settings_bg}; border-left: 1px solid {border_clr};")
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {text_primary}; letter-spacing: -1px;")

    def _on_lang_changed(self, lang_code):
        self._current_lang_code = lang_code
        # Localize UI
        self.retranslate_ui(lang_code)
        
        t = self.TRANSLATIONS.get(lang_code, self.TRANSLATIONS["en"])
        sample = t["sample_text"]

        # Only set sample if editor is empty or currently shows another sample
        current_text = self.text_editor.toPlainText().strip()
        is_current_a_sample = False
        for lang in self.TRANSLATIONS.values():
            if current_text == lang["sample_text"].strip():
                is_current_a_sample = True
                break
        
        if not current_text or is_current_a_sample:
            self._is_sample_active = True
            self.text_editor.blockSignals(True)
            self.text_editor.setText(sample)
            self.text_editor.setStyleSheet(self.text_editor.styleSheet() + " color: #555;")
            self.text_editor.blockSignals(False)

    def _on_paste(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self._is_sample_active = False
            self.text_editor.setStyleSheet(self.text_editor.styleSheet().replace(" color: #555;", " color: #fff;"))
            self.text_editor.setText(text)

    def _handle_text_edit(self):
        if self._is_sample_active:
            # Detect if user actually typed something
            t = self.TRANSLATIONS.get(self._current_lang_code, self.TRANSLATIONS["en"])
            sample = t["sample_text"]
            current = self.text_editor.toPlainText()
            
            # if current text is no longer exactly the sample, user started edit
            if current != sample:
                self._is_sample_active = False
                # Remove the sample's dimmed color
                self.text_editor.setStyleSheet(self.text_editor.styleSheet().replace(" color: #555;", " color: #fff;"))
                
                # If the user typed a character, we want to keep ONLY that character
                # and remove the rest of the sample text that might still be there.
                # Simplest way: if length changed slightly, assume they typed 1 char.
                if len(current) > 0:
                    # Find the new character or just clear and let them start fresh?
                    # Usually placeholders clear entirely. 
                    # Let's find the new char by removing the sample part if possible, 
                    # or just clear if the user prefers a clean slate.
                    # User said: "üstüne yazmaya başladığımda otomatik olarak silinsin"
                    # I will clear it and keep what they just typed.
                    new_char = current.replace(sample, "") if sample in current else current[-1:]
                    self.text_editor.blockSignals(True)
                    self.text_editor.setText(new_char)
                    # Move cursor to end
                    cursor = self.text_editor.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)
                    self.text_editor.setTextCursor(cursor)
                    self.text_editor.blockSignals(False)

    def _on_start(self):
        text = self.text_editor.toPlainText().strip()
        lang = self._current_lang_code
        if text:
            self.start_requested.emit(text, lang)
