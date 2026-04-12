"""Application state management."""


class StateManager:
    """Centralized app state."""

    def __init__(self):
        self.current_screen = "home" 
        self.voice_listening = False
        self.hand_tracking_active = True
        self.last_command = ""
        self.notifications = []

    def set_screen(self, screen_name):
        self.current_screen = screen_name

    def add_notification(self, message, level="info"):
        self.notifications.append({"message": message, "level": level})
        if len(self.notifications) > 5:
            self.notifications.pop(0)


state = StateManager()