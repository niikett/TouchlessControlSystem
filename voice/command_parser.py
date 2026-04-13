import re
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Represents a parsed voice command."""

    category: str
    action: str
    value: str | None
    raw_text: str


class CommandParser:
    """
    Parses raw voice text into structured commands.
    """

    VOLUME_KEYWORDS = {
        "full": 100,
        "max": 100,
        "maximum": 100,
        "half": 50,
        "low": 25,
        "min": 10,
        "minimum": 10,
        "zero": 0,
    }

    APP_KEYWORDS = {
        "whatsapp": "whatsapp",
        "what's app": "whatsapp",
        "google": "google_search",
        "google search": "google_search",
        "search": "google_search",
        "maps": "maps",
        "map": "maps",
        "google maps": "maps",
        "spotify": "spotify",
        "music": "spotify",
        "youtube": "youtube",
        "you tube": "youtube",
        "home": "home",
        "main menu": "home",
    }

    def parse(self, text: str) -> ParsedCommand:
        text = text.lower().strip()

        parsers = [
            self._parse_volume,
            self._parse_mute,
            self._parse_maps_directions,
            self._parse_maps_search,
            self._parse_start_navigation,
            self._parse_youtube,
            self._parse_spotify,
            self._parse_open_app,
            self._parse_search,
            self._parse_whatsapp_send,
            self._parse_close,
        ]

        for parser in parsers:
            result = parser(text)
            if result:
                return result

        return ParsedCommand(
            category="unknown",
            action="unknown",
            value=text,
            raw_text=text,
        )

    # ── YouTube ──────────────────────────────────────────

    def _parse_youtube(self, text: str) -> ParsedCommand | None:
        """
        Matches:
          - "play <query> on youtube"
          - "youtube play <query>"
          - "search youtube for <query>"
          - "youtube search <query>"
          - "pause youtube" / "resume youtube"
          - "open youtube"
        """
        # Play on YouTube: "play lofi music on youtube"
        match = re.search(
            r"play\s+(.+?)\s+on\s+(?:youtube|you\s*tube)", text
        )
        if match:
            return ParsedCommand(
                "youtube", "play", match.group(1).strip(), text
            )

        # YouTube play: "youtube play lofi music"
        match = re.search(
            r"(?:youtube|you\s*tube)\s+play\s+(.+)", text
        )
        if match:
            return ParsedCommand(
                "youtube", "play", match.group(1).strip(), text
            )

        # Search YouTube: "search youtube for cooking recipes"
        match = re.search(
            r"(?:search|find|look\s*up)\s+(?:on\s+)?(?:youtube|you\s*tube)"
            r"\s+(?:for\s+)?(.+)",
            text,
        )
        if match:
            return ParsedCommand(
                "youtube", "search", match.group(1).strip(), text
            )

        # YouTube search: "youtube search cooking recipes"
        match = re.search(
            r"(?:youtube|you\s*tube)\s+(?:search|find)\s+(?:for\s+)?(.+)",
            text,
        )
        if match:
            return ParsedCommand(
                "youtube", "search", match.group(1).strip(), text
            )

        # Pause YouTube
        if re.search(
            r"(?:pause|stop)\s+(?:youtube|you\s*tube)", text
        ):
            return ParsedCommand("youtube", "pause", None, text)

        # Resume YouTube
        if re.search(
            r"(?:resume|unpause|continue)\s+(?:youtube|you\s*tube)",
            text,
        ):
            return ParsedCommand("youtube", "resume", None, text)

        # Fullscreen YouTube
        if re.search(
            r"(?:fullscreen|full\s*screen)\s+(?:youtube|you\s*tube)",
            text,
        ):
            return ParsedCommand(
                "youtube", "fullscreen", None, text
            )

        # "open youtube" is handled by _parse_open_app via APP_KEYWORDS
        return None

    # ── Spotify ──────────────────────────────────────────

    def _parse_spotify(self, text: str) -> ParsedCommand | None:
        """
        Matches:
        - "play", "pause", "resume"
        - "next song", "next track"
        - "previous song", "previous track"
        - "play Blinding Lights"
        - "play song Blinding Lights"
        - "spotify volume 80"
        """
        # Play specific song — but NOT if "on youtube" is present
        match = re.search(
            r"play\s+(?:song\s+|track\s+)?(.+)", text
        )
        if match:
            query = match.group(1).strip()
            if (
                query
                and "map" not in query
                and "volume" not in query
                and "youtube" not in query
                and "you tube" not in query
            ):
                return ParsedCommand(
                    "spotify", "search_play", query, text
                )

        # Pause
        if re.search(
            r"\b(pause|stop\s+music|pause\s+music)\b", text
        ):
            return ParsedCommand("spotify", "pause", None, text)

        # Resume
        if re.search(
            r"\b(resume|resume\s+music|unpause)\b", text
        ):
            return ParsedCommand("spotify", "resume", None, text)

        # Next
        if re.search(r"\b(next\s+(?:song|track)|skip)\b", text):
            return ParsedCommand("spotify", "next", None, text)

        # Previous
        if re.search(
            r"\b(previous\s+(?:song|track)|go\s+back\s+song)\b",
            text,
        ):
            return ParsedCommand(
                "spotify", "previous", None, text
            )

        # Spotify volume
        match = re.search(r"spotify\s+volume\s+(\d{1,3})", text)
        if match:
            level = min(100, max(0, int(match.group(1))))
            return ParsedCommand(
                "spotify", "volume", str(level), text
            )

        return None

    # ── Volume ───────────────────────────────────────────

    def _parse_volume(self, text: str) -> ParsedCommand | None:
        if re.search(
            r"(volume up|increase volume|louder|raise volume)",
            text,
        ):
            return ParsedCommand("volume", "up", "10", text)

        if re.search(
            r"(volume down|decrease volume|quieter|lower volume)",
            text,
        ):
            return ParsedCommand("volume", "down", "10", text)

        match = re.search(
            r"(?:set\s+)?volume\s+(?:to\s+)?(\d{1,3})\s*%?"
            r"\s*(?:percent)?",
            text,
        )
        if match:
            value = min(100, max(0, int(match.group(1))))
            return ParsedCommand("volume", "set", str(value), text)

        for keyword, percent in self.VOLUME_KEYWORDS.items():
            if re.search(rf"volume\s+{keyword}", text):
                return ParsedCommand(
                    "volume", "set", str(percent), text
                )

        return None

    def _parse_mute(self, text: str) -> ParsedCommand | None:
        if re.search(r"\b(unmute|un-mute)\b", text):
            return ParsedCommand("volume", "unmute", None, text)

        if re.search(r"\b(mute|shut up|silence)\b", text):
            return ParsedCommand("volume", "mute", None, text)

        return None

    # ── Maps ─────────────────────────────────────────────

    def _parse_maps_directions(
        self, text: str
    ) -> ParsedCommand | None:
        match = re.search(
            r"(?:directions?\s+to|navigate\s+to|take\s+me\s+to)"
            r"\s+(.+)",
            text,
        )
        if match:
            destination = match.group(1).strip()
            return ParsedCommand(
                "maps", "directions", destination, text
            )
        return None

    def _parse_maps_search(
        self, text: str
    ) -> ParsedCommand | None:
        match = re.search(
            r"(?:search|find|show|locate)\s+(.+?)\s*"
            r"(?:near\s*(?:me|by|here)|nearby)",
            text,
        )
        if match:
            query = match.group(1).strip()
            return ParsedCommand(
                "maps", "search_nearby", query, text
            )
        return None

    def _parse_start_navigation(
        self, text: str
    ) -> ParsedCommand | None:
        if re.search(
            r"\b(start|begin|commence)\s+"
            r"(directions?|navigation|navigating|route)\b",
            text,
        ):
            return ParsedCommand(
                "maps", "start_navigation", None, text
            )
        return None

    # ── Apps / Search / WhatsApp / System ────────────────

    def _parse_open_app(self, text: str) -> ParsedCommand | None:
        match = re.search(
            r"(?:open|launch|go\s+to|show|start)\s+(.+)", text
        )
        if match:
            app_name = match.group(1).strip()
            for keyword, app_id in self.APP_KEYWORDS.items():
                if keyword in app_name:
                    return ParsedCommand(
                        "open", "open_app", app_id, text
                    )
        return None

    def _parse_search(self, text: str) -> ParsedCommand | None:
        match = re.search(
            r"(?:search\s+(?:for\s+)?|google\s+|look\s+up\s+)"
            r"(.+)",
            text,
        )
        if match:
            query = match.group(1).strip()
            if (
                "near me" not in query
                and "nearby" not in query
                and "youtube" not in query
                and "you tube" not in query
            ):
                return ParsedCommand(
                    "search", "google", query, text
                )
        return None

    def _parse_whatsapp_send(
        self, text: str
    ) -> ParsedCommand | None:
        match = re.search(
            r"(?:send\s+(?:a\s+)?message\s+to|whatsapp|message)"
            r"\s+(\w+)\s+(?:saying|that|message)?\s*(.+)",
            text,
        )
        if match:
            contact = match.group(1).strip()
            message = match.group(2).strip()
            return ParsedCommand(
                "whatsapp",
                "send",
                f"{contact}|{message}",
                text,
            )
        return None

    def _parse_translate(self, text: str) -> ParsedCommand | None:
        match = re.search(
            r"translate\s+(.+?)\s+(?:to|in|into)\s+(\w+)", text
        )
        if match:
            phrase = match.group(1).strip()
            target_lang = match.group(2).strip()
            return ParsedCommand(
                "translate",
                "translate",
                f"{phrase}|{target_lang}",
                text,
            )
        return None

    def _parse_close(self, text: str) -> ParsedCommand | None:
        if re.search(
            r"\b(close|go\s*back|back|exit|go\s*home)\b", text
        ):
            return ParsedCommand("system", "close", None, text)
        return None