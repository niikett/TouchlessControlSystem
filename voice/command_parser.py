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
        # Play specific song
        match = re.search(
            r"play\s+(?:song\s+|track\s+)?(.+)", text
        )
        if match:
            query = match.group(1).strip()
            # Avoid matching "play" alone or maps/volume commands
            if query and "map" not in query and "volume" not in query:
                return ParsedCommand("spotify", "search_play", query, text)

        # Pause
        if re.search(r"\b(pause|stop\s+music|pause\s+music)\b", text):
            return ParsedCommand("spotify", "pause", None, text)

        # Resume
        if re.search(r"\b(resume|resume\s+music|unpause)\b", text):
            return ParsedCommand("spotify", "resume", None, text)

        # Next
        if re.search(r"\b(next\s+(?:song|track)|skip)\b", text):
            return ParsedCommand("spotify", "next", None, text)

        # Previous
        if re.search(r"\b(previous\s+(?:song|track)|go\s+back\s+song)\b", text):
            return ParsedCommand("spotify", "previous", None, text)

        # Spotify volume
        match = re.search(r"spotify\s+volume\s+(\d{1,3})", text)
        if match:
            level = min(100, max(0, int(match.group(1))))
            return ParsedCommand("spotify", "volume", str(level), text)

        return None

    def _parse_volume(self, text: str) -> ParsedCommand | None:
        """
        Matches:
          - "volume 50%", "volume 50 percent", "volume 50"
          - "volume full", "volume max", "volume half", "volume low"
          - "set volume to 80"
          - "volume up", "volume down"
          - "increase volume", "decrease volume"
        """
        
        if re.search(r"(volume up|increase volume|louder|raise volume)", text):
            return ParsedCommand("volume", "up", "10", text)

        if re.search(r"(volume down|decrease volume|quieter|lower volume)", text):
            return ParsedCommand("volume", "down", "10", text)

        match = re.search(
            r"(?:set\s+)?volume\s+(?:to\s+)?(\d{1,3})\s*%?\s*(?:percent)?",
            text,
        )
        if match:
            value = min(100, max(0, int(match.group(1))))
            return ParsedCommand("volume", "set", str(value), text)

        for keyword, percent in self.VOLUME_KEYWORDS.items():
            if re.search(rf"volume\s+{keyword}", text):
                return ParsedCommand("volume", "set", str(percent), text)

        return None

    def _parse_mute(self, text: str) -> ParsedCommand | None:
        """Matches: "mute", "unmute", "mute volume", "shut up" """
        if re.search(r"\b(unmute|un-mute)\b", text):
            return ParsedCommand("volume", "unmute", None, text)

        if re.search(r"\b(mute|shut up|silence)\b", text):
            return ParsedCommand("volume", "mute", None, text)

        return None

    def _parse_maps_directions(self, text: str) -> ParsedCommand | None:
        """
        Matches:
          - "directions to palladium mall"
          - "navigate to mumbai airport"
          - "take me to central park"
        """
        match = re.search(
            r"(?:directions?\s+to|navigate\s+to|take\s+me\s+to)\s+(.+)",
            text,
        )
        if match:
            destination = match.group(1).strip()
            return ParsedCommand("maps", "directions", destination, text)
        return None

    def _parse_maps_search(self, text: str) -> ParsedCommand | None:
        """
        Matches:
          - "search hospital near me"
          - "find restaurants nearby"
          - "show hotels near me"
        """
        match = re.search(
            r"(?:search|find|show|locate)\s+(.+?)\s*(?:near\s*(?:me|by|here)|nearby)",
            text,
        )
        if match:
            query = match.group(1).strip()
            return ParsedCommand("maps", "search_nearby", query, text)
        return None
    
    def _parse_start_navigation(self, text: str) -> ParsedCommand | None:
        """
        Matches:
        - "start directions"
        - "start navigation"
        - "start route"
        - "begin navigation"
        """
        if re.search(
            r"\b(start|begin|commence)\s+(directions?|navigation|navigating|route)\b",
            text,
        ):
            return ParsedCommand("maps", "start_navigation", None, text)
        return None

    def _parse_open_app(self, text: str) -> ParsedCommand | None:
        """
        Matches:
          - "open whatsapp"
          - "open google"
          - "open maps"
          - "go to translator"
          - "launch whatsapp"
        """
        match = re.search(
            r"(?:open|launch|go\s+to|show|start)\s+(.+)", text
        )
        if match:
            app_name = match.group(1).strip()
            for keyword, app_id in self.APP_KEYWORDS.items():
                if keyword in app_name:
                    return ParsedCommand("open", "open_app", app_id, text)
        return None

    def _parse_search(self, text: str) -> ParsedCommand | None:
        """
        Matches:
          - "search what is python"
          - "google how to cook pasta"
          - "look up machine learning"
        """
        match = re.search(
            r"(?:search\s+(?:for\s+)?|google\s+|look\s+up\s+)(.+)", text
        )
        if match:
            query = match.group(1).strip()
            # Make sure it's not a nearby/maps search
            if "near me" not in query and "nearby" not in query:
                return ParsedCommand("search", "google", query, text)
        return None

    def _parse_whatsapp_send(self, text: str) -> ParsedCommand | None:
        """
        Matches:
          - "send message to john saying hello"
          - "whatsapp john hello there"
          - "message john saying hi"
        """
        match = re.search(
            r"(?:send\s+(?:a\s+)?message\s+to|whatsapp|message)\s+"
            r"(\w+)\s+(?:saying|that|message)?\s*(.+)",
            text,
        )
        if match:
            contact = match.group(1).strip()
            message = match.group(2).strip()
            return ParsedCommand(
                "whatsapp", "send", f"{contact}|{message}", text
            )
        return None

    def _parse_translate(self, text: str) -> ParsedCommand | None:
        """
        Matches:
          - "translate hello to spanish"
          - "translate good morning to hindi"
        """
        match = re.search(
            r"translate\s+(.+?)\s+(?:to|in|into)\s+(\w+)", text
        )
        if match:
            phrase = match.group(1).strip()
            target_lang = match.group(2).strip()
            return ParsedCommand(
                "translate", "translate", f"{phrase}|{target_lang}", text
            )
        return None

    def _parse_close(self, text: str) -> ParsedCommand | None:
        """Matches: "close", "go back", "back", "exit", "go home" """
        if re.search(r"\b(close|go\s*back|back|exit|go\s*home)\b", text):
            return ParsedCommand("system", "close", None, text)
        return None