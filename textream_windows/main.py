import sys
import os
import json
import threading
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QTimer

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.overlay_window import OverlayWindow
from ui.main_window import MainWindow
from audio_engine import AudioEngine
from fuzzy_matcher import FuzzyMatcher
from download_model import download_language, MODELS 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAMPLE_TEXTS = {
    "tr": "Merhaba dünya, bu bir Textream Windows test metnidir. Sesinizi algılayarak metni otomatik olarak ilerletir.",
    "en": "Hello world, this is a Textream Windows test text. It automatically advances the text by recognizing your voice.",
    "es": "Hola mundo, este es un texto de prueba de Textream Windows. Avanza automáticamente el texto al reconocer su voz.",
    "fr": "Bonjour le monde, ceci est un texte de test Textream Windows. Il fait avancer automatiquement le texte en reconnaissant votre voix.",
    "de": "Hallo Welt, dies ist ein Textream Windows Testtext. Er bewegt den Text automatisch vorwärts, indem er Ihre Stimme erkennt.",
    "cn": "你好世界，这是 Textream Windows 测试文本。它通过识别您的声音自动推进文本。"
}

class Bridge(QObject):
    """Bridge between background Audio thread and Main UI thread."""
    result_received = pyqtSignal(str, bool) # text, is_final
    audio_level_received = pyqtSignal(float)
    model_loaded = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

def main():
    # Fix for Windows Taskbar/Task Manager icon grouping
    if sys.platform == 'win32':
        import ctypes
        myappid = 'fka.textream.windows.1.0' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    app.setApplicationName("Textream Windows")
    
    # Set official icon from the project assets
    root_dir = BASE_DIR
    icon_path = os.path.join(root_dir, "assets", "icon.png")
    app_icon = None
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # 1. Initialize Components
    matcher = FuzzyMatcher()
    main_window = MainWindow()
    if app_icon:
        main_window.setWindowIcon(app_icon)
    overlay_window = OverlayWindow()
    if app_icon:
        overlay_window.setWindowIcon(app_icon)

    # Setup Audio
    audio = AudioEngine()
    bridge = Bridge()
    
    # Show main setup window first
    main_window.show()

    # --- Background Model Pre-download ---
    def background_download_all_models():
        print("Checking/Downloading all models in background...")
        for lang in MODELS:
            if not os.path.exists(os.path.join(BASE_DIR, "models", lang)):
                # Skip TR if legacy 'model' exists
                if lang == "tr" and os.path.exists(os.path.join(BASE_DIR, "model")):
                    continue
                threading.Thread(target=download_language, args=(lang, BASE_DIR), daemon=True).start()

    # Wait a bit before starting background downloads to not lag startup
    QTimer.singleShot(5000, background_download_all_models)
    
    # --- Callbacks & Signals ---
    
    def on_audio_level(level):
        bridge.audio_level_received.emit(level)
        
    def on_audio_result(text, is_final):
        bridge.result_received.emit(text, is_final)

    audio.on_audio_level = on_audio_level
    audio.on_result = on_audio_result
    
    def on_result(text, is_final):
        if not text.strip(): return
        
        # Match current text
        char_count = matcher.match(text)
        overlay_window.update_progress(char_count)
        
        print(f"[{'FINAL' if is_final else 'PARTIAL'}] Spoken: {text} | Pos: {char_count}")

        # Only update the starting anchor when a sentence is fully finished
        if is_final:
            matcher.match_start_offset = matcher.recognized_char_count
            print(f"Anchor moved to: {matcher.match_start_offset}")

    bridge.result_received.connect(on_result)
    bridge.audio_level_received.connect(overlay_window.update_audio)
    

    
    # --- Controls & Navigation ---
    current_requested_lang = [None] # Mutable container

    def on_model_downloaded(success):
        if success and current_requested_lang[0]:
            print(f"Download finished. Loading {current_requested_lang[0]}...")
            # Re-call on_language_change_requested to load the now-present model
            on_language_change_requested(current_requested_lang[0])
            overlay_window.set_text(f"Dil İndirildi: {current_requested_lang[0]}. Başlatılıyor...")
        else:
            overlay_window.set_text("İndirme sırasında bir hata oluştu veya iptal edildi.")

    def on_bridge_error(msg):
        QMessageBox.warning(overlay_window, "Hata", msg)

    bridge.model_loaded.connect(on_model_downloaded)
    bridge.error_occurred.connect(on_bridge_error)

    def on_pause_requested(is_paused):
        if is_paused:
            audio.pause()
            print("Audio processing PAUSED")
        else:
            audio.resume()
            print("Audio processing RESUMED")

    def on_mic_toggled(is_on):
        audio.set_mic_enabled(is_on)
        print(f"Microphone {'ENABLED' if is_on else 'DISABLED'}")

    def on_rewind_requested():
        # Jump back by one word
        new_pos = matcher.get_prev_word_offset()
        matcher.jump_to(new_pos)
        overlay_window.update_progress(new_pos)
        print(f"Rewind: Jumped to {new_pos}")

    def on_forward_requested():
        # Jump forward by one word
        new_pos = matcher.get_next_word_offset()
        matcher.jump_to(new_pos)
        overlay_window.update_progress(new_pos)
        print(f"Forward: Jumped to {new_pos}")

    def on_auto_advance():
        # Advance by 1 character (timer determines frequency)
        new_pos = min(len(matcher.source_text), matcher.recognized_char_count + 1)
        matcher.jump_to(new_pos)
        overlay_window.update_progress(new_pos)

    # --- Language Change ---
    def on_language_change_requested(lang_code, load_sample=True):
        print(f"Switching language to: {lang_code}")
        current_requested_lang[0] = lang_code
        overlay_window.current_language = lang_code # Update UI state
        
        # Check if model exists
        model_path = os.path.join(BASE_DIR, "models", lang_code)
        legacy_path = os.path.join(BASE_DIR, "model")
        
        if not os.path.exists(model_path) and not (lang_code == 'tr' and os.path.exists(legacy_path)):
            # Ask user to download
            reply = QMessageBox.question(overlay_window, "Model Eksik", 
                                        f"'{lang_code}' dili için gerekli dosyalar yüklü değil.\nŞimdi indirmek ister misiniz?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                overlay_window.set_text(f"İndiriliyor: {lang_code}...\nLütfen bekleyin (Konsoldan takip edebilirsiniz).")
                def download_worker():
                    success = download_language(lang_code, BASE_DIR)
                    bridge.model_loaded.emit(success)

                threading.Thread(target=download_worker, daemon=True).start()
                return # Wait for download
            else:
                return

        # Restart Audio
        audio.stop()
        if audio.load_model(lang_code):
            audio.start()
            
            # Load Sample Text ONLY if requested (e.g. user manually switched lang via menu)
            if load_sample:
                sample = SAMPLE_TEXTS.get(lang_code, SAMPLE_TEXTS["en"])
                matcher.set_text(sample)
                overlay_window.set_text(sample)
                print(f"Sample text loaded for {lang_code}")
        else:
             QMessageBox.critical(overlay_window, "Hata", f"{lang_code} dili yüklenemedi.")

    def on_start_requested_wrapper(text, lang_code):
        main_window.hide()
        matcher.set_text(text)
        overlay_window.set_text(text)
        overlay_window.show()
        
        # Load the language selected in setup, but PRESERVE the text we just set
        on_language_change_requested(lang_code, load_sample=False)

    main_window.start_requested.connect(on_start_requested_wrapper)

    overlay_window.prompter.pause_requested.connect(on_pause_requested)
    overlay_window.prompter.mic_toggled.connect(on_mic_toggled)
    overlay_window.prompter.rewind_requested.connect(on_rewind_requested)
    overlay_window.prompter.forward_requested.connect(on_forward_requested)
    overlay_window.prompter.auto_advance_requested.connect(on_auto_advance)
    # When user changes language from overlay menu, we DO want to load sample text
    overlay_window.prompter.language_changed.connect(lambda l: on_language_change_requested(l, load_sample=True))
    overlay_window.language_changed.connect(lambda l: on_language_change_requested(l, load_sample=True))

    # Initial Load
    # Try loading 'tr' by default or 'model'
    legacy_model = os.path.join(BASE_DIR, "model")
    models_dir = os.path.join(BASE_DIR, "models")
    
    if os.path.exists(legacy_model) or os.path.exists(os.path.join(models_dir, "tr")):
        audio.load_model("tr")
        # Don't start audio yet, wait for user to hit Start in main_window
    else:
        # Try finding any model in models/
        if os.path.exists(models_dir):
            avail = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
            if avail:
                audio.load_model(avail[0])

    try:
        sys.exit(app.exec())
    finally:
        audio.stop()

if __name__ == "__main__":
    main()
