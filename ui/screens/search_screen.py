"""Google Search screen with embedded browser and persistent sign-in."""

import os

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEnginePage,
    QWebEngineProfile,
)


class SearchScreen(QWidget):
    """Embedded browser search screen with persistent login."""

    def __init__(self, back_callback, parent=None):
        super().__init__(parent)
        self.back_callback = back_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(8)

        top = QHBoxLayout()

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("hudButton")
        back_btn.setFixedSize(100, 40)
        back_btn.clicked.connect(back_callback)
        back_btn.setCursor(Qt.PointingHandCursor)

        self.nav_back_btn = QPushButton("◀")
        self.nav_back_btn.setObjectName("hudButton")
        self.nav_back_btn.setFixedSize(40, 40)
        self.nav_back_btn.setCursor(Qt.PointingHandCursor)

        self.nav_forward_btn = QPushButton("▶")
        self.nav_forward_btn.setObjectName("hudButton")
        self.nav_forward_btn.setFixedSize(40, 40)
        self.nav_forward_btn.setCursor(Qt.PointingHandCursor)

        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setObjectName("hudButton")
        self.refresh_btn.setFixedSize(40, 40)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)

        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("hudInput")
        self.url_bar.setFixedHeight(40)
        self.url_bar.setPlaceholderText("Search or enter URL...")
        self.url_bar.returnPressed.connect(self._navigate)

        self.home_btn = QPushButton("🏠")
        self.home_btn.setObjectName("hudButton")
        self.home_btn.setFixedSize(40, 40)
        self.home_btn.setCursor(Qt.PointingHandCursor)

        top.addWidget(back_btn)
        top.addSpacing(10)
        top.addWidget(self.nav_back_btn)
        top.addWidget(self.nav_forward_btn)
        top.addWidget(self.refresh_btn)
        top.addWidget(self.url_bar)
        top.addWidget(self.home_btn)

        layout.addLayout(top)

        self._setup_browser()

        layout.addWidget(self.browser)

        self.status = QLabel("Ready")
        self.status.setObjectName("hudLabel")
        self.status.setFixedHeight(20)
        layout.addWidget(self.status)

        self.nav_back_btn.clicked.connect(self.browser.back)
        self.nav_forward_btn.clicked.connect(self.browser.forward)
        self.refresh_btn.clicked.connect(self.browser.reload)
        self.home_btn.clicked.connect(self._go_google)
        self.browser.urlChanged.connect(self._on_url_changed)
        self.browser.loadStarted.connect(
            lambda: self.status.setText("Loading...")
        )
        self.browser.loadFinished.connect(self._on_load_finished)

    def _setup_browser(self):
        """Create browser with persistent profile (shared sign-in)."""
        profile_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "browser_data",
            "search_profile",
        )
        profile_path = os.path.normpath(profile_path)
        os.makedirs(profile_path, exist_ok=True)

        self.profile = QWebEngineProfile(
            "search_persistent", self
        )
        self.profile.setPersistentStoragePath(profile_path)
        self.profile.setCachePath(
            os.path.join(profile_path, "cache")
        )
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.ForcePersistentCookies
        )

        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        self.page = QWebEnginePage(self.profile, self)

        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.browser.setStyleSheet(
            "background-color: white; border-radius: 10px;"
        )
        self.browser.setUrl(QUrl("https://www.google.com"))

    def _navigate(self):
        """Navigate to URL or search query."""
        text = self.url_bar.text().strip()
        if not text:
            return

        if "." in text and " " not in text:
            if not text.startswith("http"):
                text = "https://" + text
            self.browser.setUrl(QUrl(text))
        else:
            search_url = (
                f"https://www.google.com/search?q={text}"
            )
            self.browser.setUrl(QUrl(search_url))

    def _go_google(self):
        """Navigate to Google home."""
        self.browser.setUrl(QUrl("https://www.google.com"))

    def _on_url_changed(self, url):
        """Update URL bar when page changes."""
        self.url_bar.setText(url.toString())

    def _on_load_finished(self, ok):
        """Update status when page loads."""
        if ok:
            title = self.browser.page().title()
            self.status.setText(f"✓ {title}")
        else:
            self.status.setText("✗ Failed to load")

    def search_from_voice(self, query):
        """Programmatic search from voice command."""
        self.url_bar.setText(query)
        search_url = (
            f"https://www.google.com/search?q={query}"
        )
        self.browser.setUrl(QUrl(search_url))

    def perform_search(self, query):
        """Alias for voice-triggered search."""
        self.search_from_voice(query)