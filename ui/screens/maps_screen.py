"""Maps screen with embedded Google Maps and persistent sign-in."""

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


class MapsScreen(QWidget):
    """Embedded Google Maps screen with persistent login."""

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

        title = QLabel("🗺️ Maps")
        title.setObjectName("hudTitle")
        font = QFont("Segoe UI", 16, QFont.Light)
        title.setFont(font)

        top.addWidget(back_btn)
        top.addSpacing(10)
        top.addWidget(title)
        top.addStretch()

        layout.addLayout(top)

        search_row = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setObjectName("hudInput")
        self.search_input.setFixedHeight(40)
        self.search_input.setPlaceholderText(
            "Search places or get directions..."
        )
        self.search_input.returnPressed.connect(self._search_place)

        search_btn = QPushButton("🔍")
        search_btn.setObjectName("hudButton")
        search_btn.setFixedSize(50, 40)
        search_btn.clicked.connect(self._search_place)
        search_btn.setCursor(Qt.PointingHandCursor)

        search_row.addWidget(self.search_input)
        search_row.addWidget(search_btn)

        layout.addLayout(search_row)

        quick_row = QHBoxLayout()
        quick_row.setSpacing(8)

        quick_actions = [
            ("🏥 Hospital", "hospitals near me"),
            ("⛽ Petrol", "petrol stations near me"),
            ("🍕 Food", "restaurants near me"),
            ("🏧 ATM", "atm near me"),
            ("🏪 Store", "stores near me"),
            ("📍 My Location", "__my_location__"),
        ]

        for label, query in quick_actions:
            btn = QPushButton(label)
            btn.setObjectName("hudButton")
            btn.setFixedHeight(35)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, q=query: self._quick_action(q)
            )
            quick_row.addWidget(btn)

        layout.addLayout(quick_row)

        self._setup_browser()

        layout.addWidget(self.browser)

        self.status = QLabel("📍 Google Maps loaded")
        self.status.setObjectName("hudLabel")
        self.status.setFixedHeight(20)
        self.browser.loadStarted.connect(
            lambda: self.status.setText("Loading map...")
        )
        self.browser.loadFinished.connect(self._on_load_finished)
        layout.addWidget(self.status)

    def _setup_browser(self):
        """
        Create browser with persistent profile.
        Google sign-in and location permissions persist
        across app restarts.
        """
        profile_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "browser_data",
            "maps_profile",
        )
        profile_path = os.path.normpath(profile_path)
        os.makedirs(profile_path, exist_ok=True)

        self.profile = QWebEngineProfile(
            "maps_persistent", self
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

        self.page.featurePermissionRequested.connect(
            self._handle_permission
        )

        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.browser.setStyleSheet(
            "background-color: #1a1a2e; border-radius: 10px;"
        )

        self.browser.setUrl(QUrl("https://www.google.com/maps"))

    def _handle_permission(self, url, feature):
        """Auto-grant geolocation and other permissions."""
        if feature == QWebEnginePage.Geolocation:
            self.page.setFeaturePermission(
                url,
                feature,
                QWebEnginePage.PermissionGrantedByUser,
            )
            print(f"[MAPS] Geolocation granted for {url.host()}")
        else:
            self.page.setFeaturePermission(
                url,
                feature,
                QWebEnginePage.PermissionGrantedByUser,
            )

    def _search_place(self):
        """Search for a place on Google Maps."""
        query = self.search_input.text().strip()
        if not query:
            return
        url = f"https://www.google.com/maps/search/{query}"
        self.browser.setUrl(QUrl(url))
        self.status.setText(f"Searching: {query}")

    def _quick_action(self, query):
        """Handle quick action buttons."""
        if query == "__my_location__":
            self.browser.setUrl(
                QUrl("https://www.google.com/maps/@?api=1&map_action=map")
            )
            self.status.setText("Detecting location...")
            return

        url = f"https://www.google.com/maps/search/{query}+near+me"
        self.browser.setUrl(QUrl(url))
        self.search_input.setText(query)
        self.status.setText(f"Searching: {query}")

    def get_directions(self, destination):
        """
        Get directions from current location to destination.
        Uses Google Maps URL with dir_action=navigate to auto-start.
        """
        from urllib.parse import quote

        dest_encoded = quote(destination)

        url = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin=My+Location"
            f"&destination={dest_encoded}"
            f"&travelmode=driving"
        )
        self.browser.setUrl(QUrl(url))
        self.search_input.setText(f"Directions to {destination}")
        self.status.setText(f"🧭 Navigating to: {destination}")

    def start_navigation(self):
        """
        Click the blue Start button on Google Maps directions page.
        Tries multiple strategies to find and click it.
        """
        js_code = """
        (function() {
            // Strategy 1: Find button by visible text "Start"
            var allButtons = document.querySelectorAll('button');
            for (var i = 0; i < allButtons.length; i++) {
                var txt = allButtons[i].textContent.trim();
                if (txt === 'Start' || txt === 'Start navigation') {
                    allButtons[i].click();
                    return 'clicked: ' + txt;
                }
            }

            // Strategy 2: Find any element with "Start" text
            var walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_ELEMENT,
                null,
                false
            );
            var node;
            while (node = walker.nextNode()) {
                var text = node.textContent.trim();
                if (text === 'Start' && node.offsetParent !== null) {
                    node.click();
                    return 'walker_clicked: ' + node.tagName;
                }
            }

            // Strategy 3: Find blue colored button (Google's primary action)
            var blues = document.querySelectorAll(
                '[style*="background-color: rgb(26, 115, 232)"], '
                + '[style*="background-color:#1a73e8"], '
                + '.blue-button, '
                + '[class*="primary"], '
                + '[class*="start"]'
            );
            for (var i = 0; i < blues.length; i++) {
                if (blues[i].offsetParent !== null) {
                    blues[i].click();
                    return 'blue_clicked: ' + blues[i].tagName;
                }
            }

            // Strategy 4: Log all visible buttons for debugging
            var info = [];
            for (var i = 0; i < allButtons.length; i++) {
                if (allButtons[i].offsetParent !== null) {
                    info.push(
                        allButtons[i].textContent.trim().substring(0, 30)
                    );
                }
            }
            return 'no_start_found. Visible buttons: ' + info.join(' | ');
        })();
        """
        self.page.runJavaScript(
            js_code,
            self._on_nav_result,
        )
        self.status.setText("🧭 Starting navigation...")

    def _on_nav_result(self, result):
        """Log the result of navigation attempt."""
        print(f"[MAPS] Navigation JS result: {result}")
        if result and "clicked" in str(result):
            self.status.setText("🧭 Navigation started!")
        else:
            self.status.setText("⚠️ Could not find Start button")
            print(f"[MAPS] DEBUG: {result}")
    
    def search_nearby(self, query):
        """Search nearby places (called by voice)."""
        from urllib.parse import quote

        query_encoded = quote(query)
        url = (
            f"https://www.google.com/maps/search/"
            f"{query_encoded}+near+me"
        )
        self.browser.setUrl(QUrl(url))
        self.search_input.setText(f"{query} near me")
        self.status.setText(f"Searching: {query} near me")

    def _on_load_finished(self, ok):
        if ok:
            self.status.setText("✓ Map loaded")
        else:
            self.status.setText("✗ Failed to load map")