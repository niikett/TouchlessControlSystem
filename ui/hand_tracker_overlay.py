"""Floating hand tracker preview overlay (PiP-style)."""

import cv2
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap


class HandTrackerOverlay(QWidget):
    """Small draggable PiP window showing the hand tracker feed."""

    OVERLAY_W = 260
    OVERLAY_H = 220
    VIDEO_W = 244
    VIDEO_H = 180

    def __init__(self, tracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("overlayRoot")
        self.setFixedSize(self.OVERLAY_W, self.OVERLAY_H)

        self.setStyleSheet("""
            QWidget#overlayRoot {
                background-color: rgba(15, 20, 35, 230);
                border: 1px solid rgba(0, 200, 255, 180);
                border-radius: 10px;
            }
            QLabel#videoLabel {
                background-color: #000;
                border-radius: 6px;
                color: #888;
            }
            QLabel#headerLabel {
                color: #00c8ff;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
            }
            QPushButton#closeBtn {
                background-color: transparent;
                color: #ff5555;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#closeBtn:hover { color: #ff0000; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 8)
        layout.setSpacing(4)

        header = QHBoxLayout()
        title = QLabel("Hand Tracker")
        title.setObjectName("headerLabel")
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.hide)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        self.video_label = QLabel("Waiting for camera...")
        self.video_label.setObjectName("videoLabel")
        self.video_label.setFixedSize(self.VIDEO_W, self.VIDEO_H)
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label)

        self._drag_pos = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(33) 

    def _update_frame(self):
        if not self.isVisible():
            return
        frame = self.tracker.get_preview_frame()
        if frame is None:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.video_label.setPixmap(pix)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            new_pos = event.globalPos() - self._drag_pos
            if self.parent():
                p = self.parent()
                new_pos.setX(
                    max(0, min(new_pos.x(), p.width() - self.width()))
                )
                new_pos.setY(
                    max(0, min(new_pos.y(), p.height() - self.height()))
                )
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None