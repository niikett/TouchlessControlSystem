"""
AI Glasses - Main Entry Point
Launches the HUD interface with hand tracking.
"""
import sys
import threading
import os

# ✅ FORCE ANGLE (DirectX backend)
os.environ["QT_OPENGL"] = "angle"

# ✅ Use DirectX instead of OpenGL
os.environ["QT_ANGLE_PLATFORM"] = "d3d11"

# ✅ QtWebEngine safe flags
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-gpu "
    "--disable-software-rasterizer "
    "--no-sandbox"
)

os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
from PyQt5.QtWebEngine import QtWebEngine
QtWebEngine.initialize()

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)


import cv2
from ui.main_window import MainWindow
from hand_tracking.tracker import HandTracker
from hand_tracking.gesture_recognizer import GestureRecognizer
from hand_tracking.cursor_controller import CursorController
from config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT


def run_hand_tracking(stop_event):
    """Run hand tracking in a background thread."""
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    tracker = HandTracker()
    gesture_rec = GestureRecognizer()
    cursor = CursorController()

    print("[HAND TRACKING] Started")

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        tracker.process_frame(frame)
        landmarks = tracker.get_landmark_positions(frame)
        tips = tracker.get_finger_tips(landmarks)
        fingers_up = tracker.get_fingers_up(landmarks)
        gesture = gesture_rec.detect_gesture(tips, fingers_up)
        cursor.execute(gesture)

    tracker.release()
    cap.release()
    print("[HAND TRACKING] Stopped")

def main():
    app = QApplication(sys.argv)

    stop_event = threading.Event()
    tracking_thread = threading.Thread(
        target=run_hand_tracking,
        args=(stop_event,),
        daemon=True,
    )
    tracking_thread.start()

    window = MainWindow()
    window.show()

    exit_code = app.exec_()

    stop_event.set()
    tracking_thread.join(timeout=2)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()