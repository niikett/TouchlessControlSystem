"""WhatsApp screen with embedded WhatsApp Web."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile


class WhatsAppScreen(QWidget):
    """Embedded WhatsApp Web screen."""

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

        title = QLabel("💬 WhatsApp")
        title.setObjectName("hudTitle")
        font = QFont("Segoe UI", 16, QFont.Light)
        title.setFont(font)

        self.refresh_btn = QPushButton("⟳ Refresh")
        self.refresh_btn.setObjectName("hudButton")
        self.refresh_btn.setFixedSize(100, 40)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)

        self.new_chat_btn = QPushButton("✉ New Chat")
        self.new_chat_btn.setObjectName("hudButton")
        self.new_chat_btn.setFixedSize(110, 40)
        self.new_chat_btn.setCursor(Qt.PointingHandCursor)

        top.addWidget(back_btn)
        top.addSpacing(10)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.new_chat_btn)
        top.addWidget(self.refresh_btn)

        layout.addLayout(top)

        self.info_bar = QLabel(
            "📱 Scan the QR code with your phone to connect WhatsApp"
        )
        self.info_bar.setObjectName("hudLabel")
        self.info_bar.setAlignment(Qt.AlignCenter)
        self.info_bar.setStyleSheet(
            "background-color: rgba(0, 120, 255, 30);"
            "border: 1px solid rgba(0, 180, 255, 80);"
            "border-radius: 8px;"
            "padding: 8px;"
            "color: #00b4ff;"
        )
        self.info_bar.setFixedHeight(40)
        layout.addWidget(self.info_bar)

        self.browser = QWebEngineView()

        profile = self.browser.page().profile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.ForcePersistentCookies
        )

        self.browser.setUrl(QUrl("https://web.whatsapp.com"))
        self.browser.setStyleSheet(
            "background-color: #111b21; border-radius: 10px;"
        )

        layout.addWidget(self.browser)

        self.status = QLabel("Loading WhatsApp Web...")
        self.status.setObjectName("hudLabel")
        self.status.setFixedHeight(20)
        layout.addWidget(self.status)

        self.refresh_btn.clicked.connect(self._refresh)
        self.new_chat_btn.clicked.connect(self._new_chat)
        self.browser.loadStarted.connect(
            lambda: self.status.setText("Loading...")
        )
        self.browser.loadFinished.connect(self._on_load_finished)
        self.browser.urlChanged.connect(self._on_url_changed)

    def _refresh(self):
        """Refresh WhatsApp Web."""
        self.browser.reload()
        self.status.setText("Refreshing...")

    def _new_chat(self):
        """Open new chat interface."""
        
        self.browser.page().runJavaScript(
            """
            // Click the new chat button
            let newChatBtn = document.querySelector(
                '[data-icon="new-chat-outline"]'
            );
            if (newChatBtn) {
                newChatBtn.closest('button')
                    ? newChatBtn.closest('button').click()
                    : newChatBtn.parentElement.click();
            }
            """
        )

    def _on_load_finished(self, ok):
        if ok:
            self.status.setText("✓ WhatsApp Web loaded")
            self.info_bar.setText(
                "✓ Connected — use gestures to navigate chats"
            )
            self.info_bar.setStyleSheet(
                "background-color: rgba(0, 200, 100, 30);"
                "border: 1px solid rgba(0, 200, 100, 80);"
                "border-radius: 8px;"
                "padding: 8px;"
                "color: #00ff88;"
            )
        else:
            self.status.setText("✗ Failed to load WhatsApp")

    def _on_url_changed(self, url):
        url_str = url.toString()
        if "web.whatsapp.com" in url_str:
            self.status.setText("✓ WhatsApp Web")

    def send_message(self, contact, message):
        """
        Send a message via WhatsApp Web URL scheme.
        Called by voice commands.
        """
        
        url = (
            f"https://web.whatsapp.com/send?"
            f"phone={contact}&text={message}"
        )
        self.browser.setUrl(QUrl(url))
        self.status.setText(f"Sending to {contact}...")
        