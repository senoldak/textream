from PyQt6.QtWidgets import QMainWindow, QApplication, QMenu, QFontDialog, QColorDialog
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QAction, QFont

from .prompter_widget import PrompterWidget
from settings import settings

class OverlayWindow(QMainWindow):
    language_changed = pyqtSignal(str) # Emits language code (e.g., 'tr', 'en')

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.prompter = PrompterWidget(self)
        self.setCentralWidget(self.prompter)
        
        # Initial size
        self.update_size()
        self.center_top()

        self.prompter.setStyleSheet("background-color: transparent;")
        self.apply_theme()
        
        self.current_language = "tr"

    def apply_theme(self):
        # We can adjust colors based on settings.theme here
        self.update()

    def refresh_settings(self):
        """Syncs visuals with the latest global settings."""
        self.apply_theme()
        self.update_size()
        self.prompter.update_display()
        self.prompter.waveform.update() # Refresh waveform style/colors

    def update_size(self):
        # Calculate width based on notch feel, height based on settings
        line_height = self.prompter.text_edit.fontMetrics().lineSpacing()
        height = line_height * settings.line_count + 110 # +110 for margins, controls, and waveform
        self.resize(380, height)
        self.prompter.adjust_height()

    def center_top(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = 0 
        self.move(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        is_dark = settings.theme == "dark"
        
        if is_dark:
            bg_color = QColor(0, 0, 0, 240)
        else:
            bg_color = QColor(255, 255, 255, 245) # Light theme: creamy white
            
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 20, 20)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def show_context_menu(self, pos):
        # Localize
        from locales import TRANSLATIONS
        t = TRANSLATIONS.get(self.current_language, TRANSLATIONS["en"])

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #1a1a1a; color: #ddd; border: 1px solid #333; padding: 5px; border-radius: 8px; }
            QMenu::item { padding: 8px 25px 8px 20px; border-radius: 4px; }
            QMenu::item:selected { background-color: #2a2a2a; color: white; }
            QMenu::separator { height: 1px; background: #333; margin: 5px 0px; }
        """)
        
        # 1. Themes
        theme_menu = menu.addMenu(t["ctx_theme"])
        t_dark = QAction(t["ctx_dark"], self)
        t_dark.triggered.connect(lambda: self._update_setting("theme", "dark"))
        t_light = QAction(t["ctx_light"], self)
        t_light.triggered.connect(lambda: self._update_setting("theme", "light"))
        theme_menu.addActions([t_dark, t_light])

        # 2. Waveform Style
        wave_menu = menu.addMenu(t["ctx_wave"])
        # Map localized names from wave_styles in MainWindow logic, or just use hardcoded localized map here from locales
        # Since logic needs 'bars', 'dots' etc. we can iterate TRANSLATIONS[curr]["wave_styles"]
        wave_styles = t["wave_styles"]
        for name, val in wave_styles.items():
            act = QAction(name, self)
            act.triggered.connect(lambda checked, v=val: self._update_setting("waveform_style", v))
            wave_menu.addAction(act)

        # 3. Colors Submenu
        color_menu = menu.addMenu(t["ctx_colors"])
        presets = t["color_presets"]

        def add_color_submenu(target_menu, setting_key):
            for name, hex in presets.items():
                act = QAction(name, self)
                act.triggered.connect(lambda checked, h=hex, k=setting_key: self._update_setting(k, h))
                target_menu.addAction(act)
            target_menu.addSeparator()
            custom_act = QAction(t["ctx_custom"], self)
            custom_act.triggered.connect(lambda: self._pick_custom_color(setting_key))
            target_menu.addAction(custom_act)

        add_color_submenu(color_menu.addMenu(t["ctx_wc"]), "waveform_color")
        add_color_submenu(color_menu.addMenu(t["ctx_tc"]), "text_color")
        add_color_submenu(color_menu.addMenu(t["ctx_hc"]), "highlight_color")

        # 4. Font & Size
        font_action = QAction(t["ctx_font"], self)
        font_action.triggered.connect(self._pick_font)
        menu.addAction(font_action)

        # 5. Line Count
        line_menu = menu.addMenu(t["ctx_lines"])
        for i in range(1, 6):
            act = QAction(f"{i} {t['ctx_lines_suffix']}", self)
            act.triggered.connect(lambda checked, v=i: self._update_setting("line_count", v))
            line_menu.addAction(act)

        menu.addSeparator()

        # 6. Languages
        lang_menu = menu.addMenu(t["ctx_lang"])
        langs = t["lang_names"] # Use localized language names
        
        # Invert the map: name->code to code->name for display
        # Wait, the dict is name:code. we need code:name for iteration if we want sorted? 
        # Actually t["lang_names"] is {"Türkçe": "tr", ...}
        # We need to iterate items.
        
        curr = getattr(self, "current_language", "tr")

        for name, code in langs.items():
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(code == curr)
            action.triggered.connect(lambda checked, c=code: self.language_changed.emit(c))
            lang_menu.addAction(action)

        # 7. Position
        pos_menu = menu.addMenu(t["ctx_pos"])
        pos_actions = {
            t["ctx_top"]: self.center_top,
            t["ctx_bottom"]: self.center_bottom,
            t["ctx_center"]: self.center_screen
        }
        for label, func in pos_actions.items():
            act = QAction(label, self)
            act.triggered.connect(func)
            pos_menu.addAction(act)
        
        menu.addSeparator()

        mic_action = QAction(t["mic_on"] if self.prompter.is_mic_on else t["mic_off"], self)
        mic_action.triggered.connect(self.prompter._toggle_mic)
        menu.addAction(mic_action)

        menu.addSeparator()

        quit_action = QAction(t["ctx_quit"], self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        
        menu.exec(pos)

    def _pick_font(self):
        current_font = QFont(settings.font_family, settings.font_size)
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            settings.font_family = font.family()
            settings.font_size = font.pointSize()
            self.refresh_settings()

    def _pick_custom_color(self, setting_key):
        color = QColorDialog.getColor(QColor(getattr(settings, setting_key)), self)
        if color.isValid():
            self._update_setting(setting_key, color.name().upper())

    def _update_setting(self, key, value):
        setattr(settings, key, value)
        self.refresh_settings()
        print(f"Setting updated: {key} = {value}")


    def center_bottom(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - self.height() - 20
        self.move(x, y)

    def center_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_audio(self, level):
        self.prompter.update_audio_level(level)

    def set_text(self, text):
        self.refresh_settings() # Sync with latest global settings
        self.prompter.set_text(text)
        self.center_top()

    def update_progress(self, count):
        self.prompter.update_progress(count)
