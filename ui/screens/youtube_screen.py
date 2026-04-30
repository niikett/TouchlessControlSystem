"""YouTube screen with embedded browser and persistent sign-in."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from ui.screens.persistent_profile import get_shared_profile


class YouTubeScreen(QWidget):
    """Embedded browser YouTube screen with persistent login."""

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
        self.url_bar.setPlaceholderText("Search YouTube or enter URL...")
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
        self.home_btn.clicked.connect(self._go_youtube)
        self.browser.urlChanged.connect(self._on_url_changed)
        self.browser.loadStarted.connect(
            lambda: self.status.setText("Loading...")
        )
        self.browser.loadFinished.connect(self._on_load_finished)

        self._pending_autoplay = False

    def _setup_browser(self):
        """Create browser with shared persistent profile."""
        self.profile = get_shared_profile(self)
        self.page = QWebEnginePage(self.profile, self)

        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.browser.setStyleSheet(
            "background-color: white; border-radius: 10px;"
        )
        self.browser.setUrl(QUrl("https://www.youtube.com"))

    def _navigate(self):
        """Navigate to URL or search YouTube."""
        text = self.url_bar.text().strip()
        if not text:
            return

        if "." in text and " " not in text:
            if not text.startswith("http"):
                text = "https://" + text
            self.browser.setUrl(QUrl(text))
        else:
            search_url = (
                f"https://www.youtube.com/results?search_query={text}"
            )
            self.browser.setUrl(QUrl(search_url))

    def _go_youtube(self):
        """Navigate to YouTube home."""
        self.browser.setUrl(QUrl("https://www.youtube.com"))

    def _on_url_changed(self, url):
        """Update URL bar when page changes."""
        self.url_bar.setText(url.toString())

    def _on_load_finished(self, ok):
        """Update status when page loads."""
        if ok:
            title = self.browser.page().title()
            self.status.setText(f"✓ {title}")

            if self._pending_autoplay:
                self._pending_autoplay = False
                self._click_first_video()
        else:
            self.status.setText("✗ Failed to load")

    def _click_first_video(self):
        """Inject JS to click the first video in search results."""
        js = """
        (function() {
            var video = document.querySelector(
                'ytd-video-renderer a#video-title'
            );
            if (video) { video.click(); return true; }
            return false;
        })();
        """
        self.browser.page().runJavaScript(js)

    def search_youtube(self, query):
        """Search YouTube programmatically (voice command)."""
        self._pending_autoplay = False
        self.url_bar.setText(query)
        search_url = (
            f"https://www.youtube.com/results?search_query={query}"
        )
        self.browser.setUrl(QUrl(search_url))

    def play_video(self, query):
        """Search and auto-play first result."""
        self._pending_autoplay = True
        self.url_bar.setText(query)
        search_url = (
            f"https://www.youtube.com/results?search_query={query}"
        )
        self.browser.setUrl(QUrl(search_url))

    def toggle_play_pause(self):
        """Toggle play/pause on the current YouTube video."""
        js = """
        (function() {
            var video = document.querySelector('video');
            if (video) {
                if (video.paused) { video.play(); }
                else { video.pause(); }
            }
        })();
        """
        self.browser.page().runJavaScript(js)

    def toggle_fullscreen(self):
        """Toggle fullscreen on the current YouTube video."""
        js = """
        (function() {
            var btn = document.querySelector('.ytp-fullscreen-button');
            if (btn) { btn.click(); }
        })();
        """
        self.browser.page().runJavaScript(js)