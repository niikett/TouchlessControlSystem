"""Ground truth test cases for voice command parser."""

TEST_CASES = [
    ("volume up", "volume", "up"),
    ("volume down", "volume", "down"),
    ("set volume to 60", "volume", "set"),
    ("volume max", "volume", "set"),
    ("mute", "volume", "mute"),
    ("unmute", "volume", "unmute"),

    ("open whatsapp", "open", "open_app"),
    ("open spotify", "open", "open_app"),
    ("launch youtube", "open", "open_app"),
    ("go to maps", "open", "open_app"),
    ("open home", "open", "open_app"),

    ("search for python tutorials", "search", "google"),
    ("google best pizza", "search", "google"),
    ("look up weather", "search", "google"),

    ("directions to airport", "maps", "directions"),
    ("navigate to library", "maps", "directions"),
    ("find coffee near me", "maps", "search_nearby"),
    ("start navigation", "maps", "start_navigation"),

    ("play blinding lights", "spotify", "search_play"),
    ("pause", "spotify", "pause"),
    ("next song", "spotify", "next"),
    ("previous track", "spotify", "previous"),
    ("spotify volume 70", "spotify", "volume"),

    ("play despacito on youtube", "youtube", "play"),
    ("youtube play lofi beats", "youtube", "play"),
    ("search youtube for cats", "youtube", "search"),
    ("pause youtube", "youtube", "pause"),
    ("resume youtube", "youtube", "resume"),

    ("send message to john saying hello", "whatsapp", "send"),

    ("close", "system", "close"),
    ("go back", "system", "close"),

    ("hello world", "unknown", "unknown"),
    ("random nonsense", "unknown", "unknown"),
]