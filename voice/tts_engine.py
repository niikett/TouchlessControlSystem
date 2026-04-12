import pyttsx3
import threading


class TTSEngine:
    """Text-to-Speech engine for voice feedback."""

    def __init__(self):
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", 180)
        self._engine.setProperty("volume", 0.9)

        voices = self._engine.getProperty("voices")
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                self._engine.setProperty("voice", voice.id)
                break

        self._lock = threading.Lock()

    def speak(self, text: str):
        """Speak text in a background thread (non-blocking)."""
        thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
        thread.start()

    def _speak_sync(self, text: str):
        """Thread-safe synchronous speech."""
        with self._lock:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")

    def set_rate(self, rate: int):
        self._engine.setProperty("rate", rate)

    def set_volume(self, volume: float):
        """Set TTS volume (0.0 to 1.0)."""
        self._engine.setProperty("volume", max(0.0, min(1.0, volume)))