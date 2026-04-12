import speech_recognition as sr
import threading
import time


class VoiceListener:
    """
    Continuously listens for voice commands using the microphone.
    Runs in a background thread and calls a callback with recognized text.
    """

    def __init__(self, on_command_callback, on_status_callback=None):
        """
        Args:
            on_command_callback: function(str) called with recognized text
            on_status_callback: function(str) called with status updates
        """
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.on_command = on_command_callback
        self.on_status = on_status_callback or (lambda s: None)
        self.is_listening = False
        self._thread = None
        self._stop_event = threading.Event()

        with self.microphone as source:
            self.on_status("Calibrating microphone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.on_status("Microphone ready.")

        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

    def start(self):
        """Start listening in a background thread."""
        if self.is_listening:
            return
        self.is_listening = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        self.on_status("🎙️ Voice listener active")

    def stop(self):
        """Stop the listener."""
        self.is_listening = False
        self._stop_event.set()
        self.on_status("🎙️ Voice listener stopped")

    def _listen_loop(self):
        """Main listening loop running in background thread."""
        while not self._stop_event.is_set():
            try:
                with self.microphone as source:
                    self.on_status("🎙️ Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)

                self.on_status("🔄 Processing speech...")

                try:
                    text = self.recognizer.recognize_google(audio).lower().strip()
                    if text:
                        self.on_status(f'✅ Heard: "{text}"')
                        self.on_command(text)
                except sr.UnknownValueError:
                    self.on_status("🔇 Didn't catch that")
                except sr.RequestError as e:
                    self.on_status(f"❌ API error: {e}")

            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                self.on_status(f"❌ Listener error: {e}")
                time.sleep(1)

    def listen_once(self) -> str | None:
        """
        Single blocking listen. Useful for one-shot commands.
        Returns recognized text or None.
        """
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
            text = self.recognizer.recognize_google(audio).lower().strip()
            return text
        except (sr.UnknownValueError, sr.WaitTimeoutError, sr.RequestError):
            return None