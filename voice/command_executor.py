from voice.command_parser import ParsedCommand
from voice.tts_engine import TTSEngine
from utils.system_controls import (
    set_volume,
    get_volume,
    mute,
    unmute,
    is_muted,
)


class CommandExecutor:
    """
    Executes parsed commands by dispatching to appropriate modules.
    Connects to the UI via callbacks.
    """

    def __init__(self, ui_callback=None):
        self.tts = TTSEngine()
        self.ui_callback = ui_callback or (
            lambda action, data: None
        )

    def execute(self, command: ParsedCommand):
        handlers = {
            "volume": self._handle_volume,
            "open": self._handle_open,
            "search": self._handle_search,
            "maps": self._handle_maps,
            "whatsapp": self._handle_whatsapp,
            "spotify": self._handle_spotify,
            "youtube": self._handle_youtube,
            "system": self._handle_system,
            "unknown": self._handle_unknown,
        }
        handler = handlers.get(
            command.category, self._handle_unknown
        )
        handler(command)

    # ── YouTube ──────────────────────────────────────────

    def _handle_youtube(self, cmd: ParsedCommand):
        if cmd.action == "play":
            self.tts.speak(
                f"Playing {cmd.value} on YouTube"
            )
            self.ui_callback(
                "youtube_play", {"query": cmd.value}
            )

        elif cmd.action == "search":
            self.tts.speak(
                f"Searching YouTube for {cmd.value}"
            )
            self.ui_callback(
                "youtube_search", {"query": cmd.value}
            )

        elif cmd.action == "pause":
            self.tts.speak("Pausing YouTube")
            self.ui_callback("youtube_pause", {})

        elif cmd.action == "resume":
            self.tts.speak("Resuming YouTube")
            self.ui_callback("youtube_pause", {})

        elif cmd.action == "fullscreen":
            self.tts.speak("Toggling fullscreen")
            self.ui_callback("youtube_fullscreen", {})

    # ── Spotify ──────────────────────────────────────────

    def _handle_spotify(self, cmd: ParsedCommand):
        if cmd.action == "search_play":
            self.tts.speak(f"Playing {cmd.value}")
            self.ui_callback(
                "spotify_search", {"query": cmd.value}
            )

        elif cmd.action == "pause":
            self.tts.speak("Pausing music")
            self.ui_callback("spotify_play_pause", {})

        elif cmd.action == "resume":
            self.tts.speak("Resuming music")
            self.ui_callback("spotify_play_pause", {})

        elif cmd.action == "next":
            self.tts.speak("Next track")
            self.ui_callback("spotify_next", {})

        elif cmd.action == "previous":
            self.tts.speak("Previous track")
            self.ui_callback("spotify_previous", {})

        elif cmd.action == "volume":
            level = int(cmd.value)
            self.tts.speak(
                f"Spotify volume {level} percent"
            )
            self.ui_callback(
                "spotify_volume", {"level": level}
            )

    # ── Volume ───────────────────────────────────────────

    def _handle_volume(self, cmd: ParsedCommand):
        if cmd.action == "set":
            percent = int(cmd.value)
            set_volume(percent)
            self.tts.speak(
                f"Volume set to {percent} percent"
            )
            self.ui_callback(
                "volume_changed", {"level": percent}
            )

        elif cmd.action == "up":
            current = get_volume()
            new_vol = min(100, current + int(cmd.value))
            set_volume(new_vol)
            self.tts.speak(
                f"Volume up to {new_vol} percent"
            )
            self.ui_callback(
                "volume_changed", {"level": new_vol}
            )

        elif cmd.action == "down":
            current = get_volume()
            new_vol = max(0, current - int(cmd.value))
            set_volume(new_vol)
            self.tts.speak(
                f"Volume down to {new_vol} percent"
            )
            self.ui_callback(
                "volume_changed", {"level": new_vol}
            )

        elif cmd.action == "mute":
            mute()
            self.tts.speak("Muted")
            self.ui_callback(
                "volume_changed", {"level": 0, "muted": True}
            )

        elif cmd.action == "unmute":
            unmute()
            current = get_volume()
            self.tts.speak("Unmuted")
            self.ui_callback(
                "volume_changed",
                {"level": current, "muted": False},
            )

    # ── Open App ─────────────────────────────────────────

    def _handle_open(self, cmd: ParsedCommand):
        app_id = cmd.value
        app_names = {
            "whatsapp": "WhatsApp",
            "google_search": "Google Search",
            "maps": "Maps",
            "spotify": "Spotify",
            "youtube": "YouTube",
            "home": "Home",
        }
        name = app_names.get(app_id, app_id)
        self.tts.speak(f"Opening {name}")
        self.ui_callback("open_app", {"app": app_id})

    # ── Search ───────────────────────────────────────────

    def _handle_search(self, cmd: ParsedCommand):
        query = cmd.value
        self.tts.speak(f"Searching for {query}")
        self.ui_callback("google_search", {"query": query})

    # ── Maps ─────────────────────────────────────────────

    def _handle_maps(self, cmd: ParsedCommand):
        if cmd.action == "directions":
            self.tts.speak(
                f"Getting directions to {cmd.value}"
            )
            self.ui_callback(
                "maps_directions",
                {"destination": cmd.value},
            )
        elif cmd.action == "search_nearby":
            self.tts.speak(f"Searching {cmd.value} nearby")
            self.ui_callback(
                "maps_search", {"query": cmd.value}
            )
        elif cmd.action == "start_navigation":
            self.tts.speak("Starting navigation")
            self.ui_callback("maps_start_navigation", {})

    # ── WhatsApp ─────────────────────────────────────────

    def _handle_whatsapp(self, cmd: ParsedCommand):
        parts = cmd.value.split("|", 1)
        if len(parts) == 2:
            contact, message = parts
            self.tts.speak(
                f"Sending message to {contact}"
            )
            self.ui_callback(
                "whatsapp_send",
                {"contact": contact, "message": message},
            )
        else:
            self.tts.speak("Couldn't understand the message")

    # ── Translate ────────────────────────────────────────

    def _handle_translate(self, cmd: ParsedCommand):
        parts = cmd.value.split("|", 1)
        if len(parts) == 2:
            phrase, lang = parts
            self.tts.speak(f"Translating to {lang}")
            self.ui_callback(
                "translate",
                {"text": phrase, "target_lang": lang},
            )
        else:
            self.tts.speak(
                "Couldn't understand translation request"
            )

    # ── System ───────────────────────────────────────────

    def _handle_system(self, cmd: ParsedCommand):
        if cmd.action == "close":
            self.tts.speak("Going back")
            self.ui_callback("go_back", {})

    def _handle_unknown(self, cmd: ParsedCommand):
        self.tts.speak(
            "Sorry, I didn't understand that command"
        )
        self.ui_callback(
            "unknown_command", {"text": cmd.raw_text}
        )