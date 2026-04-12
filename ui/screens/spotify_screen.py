"""Spotify screen with embedded Spotify Web Player."""

import os

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEnginePage,
    QWebEngineProfile,
)


class SpotifyWebPage(QWebEnginePage):
    """Custom web page that grants all permissions Spotify needs."""

    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)

    def featurePermissionRequested(self, url, feature):
        """Auto-grant all permission requests from Spotify."""
        self.setFeaturePermission(
            url,
            feature,
            QWebEnginePage.PermissionGrantedByUser,
        )

    def javaScriptConsoleMessage(self, level, message, line, source):
        """Suppress JS console noise."""
        pass


class SpotifyScreen(QWidget):
    """Embedded Spotify Web Player screen."""

    def __init__(self, back_callback, parent=None):
        super().__init__(parent)
        self.back_callback = back_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(8)

        # Top bar
        top = QHBoxLayout()

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("hudButton")
        back_btn.setFixedSize(100, 40)
        back_btn.clicked.connect(back_callback)
        back_btn.setCursor(Qt.PointingHandCursor)

        title = QLabel("🎵 Spotify")
        title.setObjectName("hudTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Light))

        self.refresh_btn = QPushButton("⟳ Refresh")
        self.refresh_btn.setObjectName("hudButton")
        self.refresh_btn.setFixedSize(100, 40)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)

        self.prev_btn = QPushButton("⏮ Prev")
        self.prev_btn.setObjectName("hudButton")
        self.prev_btn.setFixedSize(90, 40)
        self.prev_btn.setCursor(Qt.PointingHandCursor)

        self.play_btn = QPushButton("⏯ Play")
        self.play_btn.setObjectName("hudButton")
        self.play_btn.setFixedSize(90, 40)
        self.play_btn.setCursor(Qt.PointingHandCursor)

        self.next_btn = QPushButton("⏭ Next")
        self.next_btn.setObjectName("hudButton")
        self.next_btn.setFixedSize(90, 40)
        self.next_btn.setCursor(Qt.PointingHandCursor)

        top.addWidget(back_btn)
        top.addSpacing(10)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.prev_btn)
        top.addWidget(self.play_btn)
        top.addWidget(self.next_btn)
        top.addSpacing(10)
        top.addWidget(self.refresh_btn)

        layout.addLayout(top)

        # Info bar
        self.info_bar = QLabel(
            "🎵 Log in with your Spotify account to start listening"
        )
        self.info_bar.setObjectName("hudLabel")
        self.info_bar.setAlignment(Qt.AlignCenter)
        self.info_bar.setStyleSheet(
            "background-color: rgba(29, 185, 84, 20);"
            "border: 1px solid rgba(29, 185, 84, 80);"
            "border-radius: 8px;"
            "padding: 8px;"
            "color: #1DB954;"
        )
        self.info_bar.setFixedHeight(40)
        layout.addWidget(self.info_bar)

        # Browser
        self._setup_browser()
        layout.addWidget(self.browser, stretch=1)

        # Status bar
        self.status = QLabel("Loading Spotify...")
        self.status.setObjectName("hudLabel")
        self.status.setFixedHeight(20)
        layout.addWidget(self.status)

        # Connect signals
        self.refresh_btn.clicked.connect(self.browser.reload)
        self.prev_btn.clicked.connect(self.on_previous)
        self.play_btn.clicked.connect(self.on_play_pause)
        self.next_btn.clicked.connect(self.on_next)
        self.browser.loadStarted.connect(
            lambda: self.status.setText("Loading...")
        )
        self.browser.loadFinished.connect(self._on_load_finished)
        self.browser.urlChanged.connect(self._on_url_changed)

    def _setup_browser(self):
        """Create browser with persistent profile for Spotify login."""
        from PyQt5.QtWebEngineWidgets import QWebEngineSettings
        from PyQt5.QtWebEngineWidgets import QWebEngineScript

        profile_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "browser_data",
            "spotify_profile",
        )
        profile_path = os.path.normpath(profile_path)
        os.makedirs(profile_path, exist_ok=True)

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentStoragePath(profile_path)
        self.profile.setCachePath(
            os.path.join(profile_path, "cache")
        )
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.ForcePersistentCookies
        )

        # Use a real Chrome user agent
        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        self.page = SpotifyWebPage(self.profile, self)

        # Enable all required settings
        settings = self.page.settings()
        settings.setAttribute(
            QWebEngineSettings.JavascriptEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.PluginsEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebGLEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.LocalStorageEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.AllowRunningInsecureContent, True
        )
        settings.setAttribute(
            QWebEngineSettings.JavascriptCanOpenWindows, True
        )
        settings.setAttribute(
            QWebEngineSettings.JavascriptCanAccessClipboard, True
        )
        settings.setAttribute(
            QWebEngineSettings.ScrollAnimatorEnabled, True
        )

        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.browser.setStyleSheet(
            "background-color: #121212; border-radius: 10px;"
        )
        self.browser.setUrl(QUrl("https://open.spotify.com"))
        self.browser.show()
        self.browser.update()   
        
    def _on_load_finished(self, ok):
        if ok:
            title = self.browser.page().title()
            self.status.setText(f"✓ {title}")
            self.info_bar.setText(
                "✓ Spotify loaded — use controls above or gestures"
            )
            self.info_bar.setStyleSheet(
                "background-color: rgba(29, 185, 84, 30);"
                "border: 1px solid rgba(29, 185, 84, 80);"
                "border-radius: 8px;"
                "padding: 8px;"
                "color: #1DB954;"
            )
        else:
            self.status.setText("✗ Failed to load Spotify")

    def _on_url_changed(self, url):
        url_str = url.toString()
        if "open.spotify.com" in url_str:
            self.status.setText("✓ Spotify Web Player")

    def on_play_pause(self):
        """Toggle play/pause via keyboard shortcut injection."""
        self.browser.page().runJavaScript(
            """
            document.dispatchEvent(new KeyboardEvent('keydown', {
                key: ' ',
                code: 'Space',
                bubbles: true
            }));
            """
        )

    def on_next(self):
        """Skip to next track."""
        self.browser.page().runJavaScript(
            """
            let nextBtn = document.querySelector(
                '[data-testid="control-button-skip-forward"]'
            );
            if (nextBtn) nextBtn.click();
            """
        )

    def on_previous(self):
        """Go to previous track."""
        self.browser.page().runJavaScript(
            """
            let prevBtn = document.querySelector(
                '[data-testid="control-button-skip-back"]'
            );
            if (prevBtn) prevBtn.click();
            """
        )

    def search_and_play(self, query: str):
        """Navigate to Spotify search for voice commands."""
        search_url = (
            f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
        )
        self.browser.setUrl(QUrl(search_url))
        self.status.setText(f"🔍 Searching: {query}")