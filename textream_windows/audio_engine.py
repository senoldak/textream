import pyaudio
import json
import math
import threading
import audioop
import os
from vosk import Model, KaldiRecognizer

class AudioEngine:
    def __init__(self):
        self.recognizer = None
        self.stream = None
        self.p = pyaudio.PyAudio()
        self.is_running = False
        self.is_paused = False
        self.is_mic_active = True
        self.on_result = None          # Callback(text, is_final)
        self.on_audio_level = None     # Callback(level_float_0_to_1)
        self.thread = None
        self.current_lang = None

    def load_model(self, lang_code="tr"):
        """Loads model for the specified language code."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "models", lang_code)
        
        # Fallback to current directory 'model' for backward compatibility
        legacy_path = os.path.join(base_dir, "model")
        if not os.path.exists(model_path) and os.path.exists(legacy_path) and lang_code == "tr":
            model_path = legacy_path
            
        if not os.path.exists(model_path):
            print(f"Error: Model not found at '{model_path}'")
            return False

        try:
            print(f"Loading model: {model_path}...")
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.current_lang = lang_code
            print("Model loaded successfully.")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False

    def start(self):
        if self.is_running: return
        
        if not self.recognizer:
            print("No model loaded. Call load_model() first.")
            return

        self.is_running = True
        self.is_paused = False
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=1024)
        
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def set_mic_enabled(self, enabled):
        self.is_mic_active = enabled

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
    def restart(self):
        """Restarts the audio stream (useful after model change)."""
        was_running = self.is_running
        self.stop()
        if was_running:
            self.start()

    def _loop(self):
        while self.is_running and self.stream:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                if len(data) == 0: break
                
                # 1. Calculate RMS for visualization (always do this if running)
                rms = audioop.rms(data, 2)
                level = min(1.0, (rms / 2000)) 
                
                if self.on_audio_level:
                    self.on_audio_level(level if (not self.is_paused and self.is_mic_active) else 0)

                # 2. Feed to Vosk only if not paused and mic is active
                if self.is_paused or not self.is_mic_active:
                    continue

                if self.recognizer.AcceptWaveform(data):
                    res = json.loads(self.recognizer.Result())
                    if 'text' in res and self.on_result:
                         self.on_result(res['text'], True)
                else:
                    res = json.loads(self.recognizer.PartialResult())
                    if 'partial' in res and self.on_result:
                        self.on_result(res['partial'], False)

            except Exception as e:
                print(f"Audio loop error: {e}")
                break
