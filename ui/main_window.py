import os
import sys
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QStackedWidget,
    QGridLayout,
    QLineEdit,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap

from core.state_manager import state
from core.event_bus import event_bus
from modules.spotify_controller import SpotifyController
from ui.hand_tracker_overlay import HandTrackerOverlay

ICONS_DIR = os.path.join(os.path.dirname(__file__), "icons")


class VoiceBridge(QObject):
    """
    Bridge between voice thread and Qt GUI thread.
    Voice commands come from a background thread,
    but GUI updates must happen on the main thread.
    Signals handle this safely.
    """

    command_signal = pyqtSignal(str, dict)
    status_signal = pyqtSignal(str)
    heard_signal = pyqtSignal(str)


class TopBar(QFrame):
    """HUD top status bar — time, status indicators."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("hudPanel")
        self.setFixedHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 5, 20, 5)

        self.status_label = QLabel("● ACTIVE")
        self.status_label.setObjectName("hudStatus")

        self.time_label = QLabel()
        self.time_label.setObjectName("hudTime")
        self.time_label.setAlignment(Qt.AlignCenter)
        font = QFont("Segoe UI", 22, QFont.Light)
        self.time_label.setFont(font)

        self.date_label = QLabel()
        self.date_label.setObjectName("hudDate")
        self.date_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self.voice_label = QLabel("● OFF")
        self.voice_label.setObjectName("hudLabel")

        layout.addWidget(self.status_label)
        layout.addSpacing(20)
        layout.addWidget(self.voice_label)
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addStretch()
        layout.addWidget(self.date_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%A, %d %B %Y"))

    def set_voice_status(self, active: bool):
        if active:
            self.voice_label.setText("● LISTENING")
            self.voice_label.setStyleSheet("color: #000000;")
        else:
            self.voice_label.setText("● OFF")
            self.voice_label.setStyleSheet("color: #000000;")


class AppButton(QPushButton):
    """A single app icon button for the home screen."""

    def __init__(self, name, icon_path, callback, parent=None):
        super().__init__(parent)
        self.setObjectName("appButton")
        self.setFixedSize(120, 120)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(callback)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            icon_label.setPixmap(
                pixmap.scaled(
                    52,
                    52,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            icon_label.setText("?")
            icon_label.setStyleSheet(
                "color: #888; font-size: 28px;"
            )

        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )
        name_label.setStyleSheet(
            "color: white; font-size: 10px;"
        )
        font = QFont("Segoe UI", 10)
        name_label.setFont(font)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(QColor(0, 150, 255, 60))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)


class HomeScreen(QWidget):
    """Main home screen with app grid."""

    def __init__(self, on_app_open, parent=None):
        super().__init__(parent)
        self.on_app_open = on_app_open

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)

        welcome = QLabel("TOUCHLESS CONTROL SYSTEM")
        welcome.setObjectName("hudTitle")
        welcome.setAlignment(Qt.AlignCenter)
        font = QFont("Segoe UI", 28, QFont.Light)
        welcome.setFont(font)
        layout.addWidget(welcome)

        subtitle = QLabel(
            "Gesture & Voice Controlled Interface"
        )
        subtitle.setObjectName("hudLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addStretch()

        app_bar = QFrame()
        app_bar.setObjectName("hudPanel")
        app_row = QHBoxLayout(app_bar)
        app_row.setSpacing(20)
        app_row.setContentsMargins(30, 20, 30, 20)
        app_row.setAlignment(Qt.AlignCenter)

        apps = [
            (
                "Google",
                os.path.join(ICONS_DIR, "search.png"),
                "search",
            ),
            (
                "Maps",
                os.path.join(ICONS_DIR, "maps.png"),
                "maps",
            ),
            (
                "WhatsApp",
                os.path.join(ICONS_DIR, "whatsapp.png"),
                "whatsapp",
            ),
            (
                "Spotify",
                os.path.join(ICONS_DIR, "spotify.png"),
                "spotify",
            ),
            (
                "YouTube",
                os.path.join(ICONS_DIR, "youtube.png"),
                "youtube",
            ),
        ]

        for name, icon, screen in apps:
            btn = AppButton(
                name,
                icon,
                lambda checked, s=screen: self.on_app_open(s),
            )
            app_row.addWidget(btn)

        layout.addWidget(app_bar)


class PlaceholderScreen(QWidget):
    """Temporary placeholder for feature screens."""

    def __init__(self, title, back_callback, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)

        top = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setObjectName("hudButton")
        back_btn.setFixedWidth(100)
        back_btn.clicked.connect(back_callback)
        back_btn.setCursor(Qt.PointingHandCursor)

        title_label = QLabel(title)
        title_label.setObjectName("hudTitle")
        font = QFont("Segoe UI", 20, QFont.Light)
        title_label.setFont(font)

        top.addWidget(back_btn)
        top.addStretch()
        top.addWidget(title_label)
        top.addStretch()
        top.addSpacing(100)

        layout.addLayout(top)
        layout.addSpacing(20)

        self.content_frame = QFrame()
        self.content_frame.setObjectName("hudPanel")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        placeholder = QLabel(
            f"{title} module will be integrated here"
        )
        placeholder.setObjectName("hudLabel")
        placeholder.setAlignment(Qt.AlignCenter)
        font2 = QFont("Segoe UI", 14)
        placeholder.setFont(font2)
        self.content_layout.addWidget(placeholder)

        layout.addWidget(self.content_frame)
        layout.addStretch()


class MainWindow(QMainWindow):
    """Main application window — the HUD."""

    def __init__(self, hand_tracker=None):
        super().__init__()

        self.hand_tracker = hand_tracker
        self.spotify_api = SpotifyController()

        self.setWindowTitle("AI Glasses")
        self.setStyleSheet(self._load_stylesheet())

        self.showFullScreen()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.top_bar = TopBar()
        main_layout.addWidget(self.top_bar)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.notif_bar = QFrame()
        self.notif_bar.setObjectName("notifBar")
        self.notif_bar.setFixedHeight(35)
        notif_layout = QHBoxLayout(self.notif_bar)
        notif_layout.setContentsMargins(15, 5, 15, 5)
        self.notif_label = QLabel(
            "System ready — gesture control active"
        )
        self.notif_label.setObjectName("hudLabel")
        notif_layout.addWidget(self.notif_label)
        main_layout.addWidget(self.notif_bar)

        self.screens = {}
        self._build_screens()

        self.go_home()

        self.shortcut_esc = self._bind_key(
            Qt.Key_Escape, self.close
        )

        self._init_voice_system()
        self._setup_hand_overlay()

    def _load_stylesheet(self):
        qss_path = os.path.join(
            os.path.dirname(__file__),
            "styles",
            "hud_theme.qss",
        )
        try:
            with open(qss_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"[WARN] Stylesheet not found: {qss_path}")
            return ""

    def _bind_key(self, key, callback):
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence

        if isinstance(key, str):
            shortcut = QShortcut(QKeySequence(key), self)
        else:
            shortcut = QShortcut(QKeySequence(key), self)
        shortcut.activated.connect(callback)
        return shortcut

    def _build_screens(self):
        from ui.screens.search_screen import SearchScreen
        from ui.screens.maps_screen import MapsScreen
        from ui.screens.whatsapp_screen import WhatsAppScreen
        from ui.screens.spotify_screen import SpotifyScreen
        from ui.screens.youtube_screen import YouTubeScreen

        home = HomeScreen(self.open_app)
        self.stack.addWidget(home)
        self.screens["home"] = home

        search = SearchScreen(self.go_home)
        self.stack.addWidget(search)
        self.screens["search"] = search

        maps = MapsScreen(self.go_home)
        self.stack.addWidget(maps)
        self.screens["maps"] = maps

        whatsapp = WhatsAppScreen(self.go_home)
        self.stack.addWidget(whatsapp)
        self.screens["whatsapp"] = whatsapp

        spotify = SpotifyScreen(self.go_home)
        self.stack.addWidget(spotify)
        self.screens["spotify"] = spotify

        youtube = YouTubeScreen(self.go_home)
        self.stack.addWidget(youtube)
        self.screens["youtube"] = youtube

    def _init_voice_system(self):
        from voice.listener import VoiceListener
        from voice.command_parser import CommandParser
        from voice.command_executor import CommandExecutor

        self.voice_bridge = VoiceBridge()
        self.voice_bridge.command_signal.connect(
            self._handle_voice_action
        )
        self.voice_bridge.status_signal.connect(
            self._handle_voice_status
        )
        self.voice_bridge.heard_signal.connect(
            self._handle_voice_heard
        )

        self.cmd_parser = CommandParser()
        self.cmd_executor = CommandExecutor(
            ui_callback=self._voice_ui_callback
        )

        self.voice_listener = VoiceListener(
            on_command_callback=self._on_voice_command,
            on_status_callback=self._on_voice_status,
        )

        self.voice_listener.start()
        self.top_bar.set_voice_status(True)
        print("[VOICE] Voice system initialized and listening")

    def _on_voice_command(self, text: str):
        self.voice_bridge.heard_signal.emit(text)
        parsed = self.cmd_parser.parse(text)
        print(f"[VOICE] Parsed: {parsed}")
        self.cmd_executor.execute(parsed)

    def _on_voice_status(self, status: str):
        self.voice_bridge.status_signal.emit(status)

    def _voice_ui_callback(self, action: str, data: dict):
        self.voice_bridge.command_signal.emit(action, data)

    def _handle_voice_heard(self, text: str):
        self.set_notification(f'🎙️ Heard: "{text}"')

    def _handle_voice_status(self, status: str):
        print(f"[VOICE] {status}")

    def _handle_voice_action(self, action: str, data: dict):
        print(f"[VOICE→UI] {action}: {data}")

        if action == "open_app":
            app_map = {
                "whatsapp": "whatsapp",
                "google_search": "search",
                "maps": "maps",
                "spotify": "spotify",
                "youtube": "youtube",
                "home": "home",
            }
            screen = app_map.get(data.get("app"), None)
            if screen:
                if screen == "home":
                    self.go_home()
                else:
                    self.open_app(screen)

        elif action == "google_search":
            query = data.get("query", "")
            self.open_app("search")
            search_screen = self.screens.get("search")
            if search_screen and hasattr(
                search_screen, "perform_search"
            ):
                search_screen.perform_search(query)

        elif action == "maps_directions":
            destination = data.get("destination", "")
            self.open_app("maps")
            maps_screen = self.screens.get("maps")
            if maps_screen and hasattr(
                maps_screen, "get_directions"
            ):
                maps_screen.get_directions(destination)

        elif action == "maps_search":
            query = data.get("query", "")
            self.open_app("maps")
            maps_screen = self.screens.get("maps")
            if maps_screen and hasattr(
                maps_screen, "search_nearby"
            ):
                maps_screen.search_nearby(query)

        elif action == "whatsapp_send":
            contact = data.get("contact", "")
            message = data.get("message", "")
            self.open_app("whatsapp")
            wa_screen = self.screens.get("whatsapp")
            if wa_screen and hasattr(wa_screen, "send_message"):
                wa_screen.send_message(contact, message)

        elif action == "spotify_play_pause":
            self.spotify_api.play_pause()

        elif action == "spotify_next":
            self.spotify_api.next()

        elif action == "spotify_previous":
            self.spotify_api.previous()

        elif action == "spotify_search":
            query = data.get("query", "")
            self.open_app("spotify")
            success = self.spotify_api.search_and_play(query)
            if not success:
                spotify_screen = self.screens.get("spotify")
                if spotify_screen:
                    spotify_screen.search_and_play(query)
                self.set_notification(
                    "⚠️ Using Web Player (Premium required)"
                )

        elif action == "spotify_volume":
            level = data.get("level", 50)
            self.spotify_api.set_volume(level)

        elif action == "youtube_search":
            query = data.get("query", "")
            self.open_app("youtube")
            yt_screen = self.screens.get("youtube")
            if yt_screen and hasattr(
                yt_screen, "search_youtube"
            ):
                yt_screen.search_youtube(query)

        elif action == "youtube_play":
            query = data.get("query", "")
            self.open_app("youtube")
            yt_screen = self.screens.get("youtube")
            if yt_screen and hasattr(yt_screen, "play_video"):
                yt_screen.play_video(query)

        elif action == "youtube_pause":
            yt_screen = self.screens.get("youtube")
            if yt_screen and hasattr(
                yt_screen, "toggle_play_pause"
            ):
                yt_screen.toggle_play_pause()

        elif action == "youtube_fullscreen":
            yt_screen = self.screens.get("youtube")
            if yt_screen and hasattr(
                yt_screen, "toggle_fullscreen"
            ):
                yt_screen.toggle_fullscreen()

        elif action == "volume_changed":
            level = data.get("level", 0)
            muted = data.get("muted", False)
            if muted:
                self.set_notification("🔇 Muted")
            else:
                self.set_notification(
                    f"🔊 Volume: {level}%"
                )

        elif action == "go_back":
            self.go_home()

        elif action == "unknown_command":
            self.set_notification(
                f"❓ Unknown command: {data.get('text', '')}"
            )

        elif action == "maps_start_navigation":
            maps_screen = self.screens.get("maps")
            if maps_screen and hasattr(
                maps_screen, "start_navigation"
            ):
                maps_screen.start_navigation()

    def open_app(self, screen_name):
        if screen_name in self.screens:
            self.stack.setCurrentWidget(self.screens[screen_name])
            state.set_screen(screen_name)
            self.notif_label.setText(f"Opened {screen_name}")
            print(f"[NAV] Opened: {screen_name}")
            if hasattr(self, "hand_overlay"):
                self.hand_overlay.raise_()

    def go_home(self):
        self.stack.setCurrentWidget(self.screens["home"])
        state.set_screen("home")
        self.notif_label.setText(
            "System ready — gesture control active"
        )
        if hasattr(self, "hand_overlay"):
            self.hand_overlay.raise_()

    def set_notification(self, message, level="info"):
        self.notif_label.setText(message)
        if level == "error":
            self.notif_bar.setObjectName("errorBar")
        else:
            self.notif_bar.setObjectName("notifBar")
        self.notif_bar.setStyleSheet(
            self.notif_bar.styleSheet()
        )

    def closeEvent(self, event):
        print("[SYSTEM] Shutting down...")
        if hasattr(self, "voice_listener"):
            self.voice_listener.stop()

        for screen_name, screen in self.screens.items():
            if hasattr(screen, "browser"):
                screen.browser.setPage(None)
            if hasattr(screen, "page"):
                screen.page.deleteLater()
            if hasattr(screen, "profile"):
                screen.profile.deleteLater()

        event.accept()

    def _setup_hand_overlay(self):
        """Create the floating hand tracker preview overlay."""
        if not self.hand_tracker:
            print("[OVERLAY] No hand tracker provided — skipping")
            return

        self.hand_overlay = HandTrackerOverlay(
            self.hand_tracker, parent=self.centralWidget()
        )
        self.hand_overlay.show()
        self._position_hand_overlay()
        self.hand_overlay.raise_()

        self._bind_key(
            "Ctrl+H", self._toggle_hand_overlay
        )

    def _position_hand_overlay(self):
        """Place overlay in bottom-right corner with margin."""
        if not hasattr(self, "hand_overlay"):
            return
        margin = 20
        parent = self.centralWidget()
        x = parent.width() - self.hand_overlay.width() - margin
        y = parent.height() - self.hand_overlay.height() - margin - 45
        self.hand_overlay.move(max(0, x), max(0, y))

    def _toggle_hand_overlay(self):
        if not hasattr(self, "hand_overlay"):
            return
        if self.hand_overlay.isVisible():
            self.hand_overlay.hide()
        else:
            self.hand_overlay.show()
            self.hand_overlay.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_hand_overlay()
        if hasattr(self, "hand_overlay"):
            self.hand_overlay.raise_()