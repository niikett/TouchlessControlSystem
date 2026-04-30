import cv2
import mediapipe as mp
import numpy as np
import threading


class HandTracker:
    """Core hand tracking using MediaPipe."""

    def __init__(
        self,
        max_hands=1,
        detection_conf=0.7,
        tracking_conf=0.7,
    ):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

        self._latest_frame = None
        self._frame_lock = threading.Lock()

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)
        return self.results

    def get_landmark_positions(self, frame, hand_index=0):
        landmarks = []
        if self.results and self.results.multi_hand_landmarks:
            if hand_index < len(self.results.multi_hand_landmarks):
                hand = self.results.multi_hand_landmarks[hand_index]
                h, w, _ = frame.shape
                for idx, lm in enumerate(hand.landmark):
                    px, py = int(lm.x * w), int(lm.y * h)
                    landmarks.append((idx, px, py))
        return landmarks

    def get_finger_tips(self, landmarks):
        if not landmarks:
            return {}
        tip_ids = {
            "thumb": 4, "index": 8, "middle": 12,
            "ring": 16, "pinky": 20,
        }
        tips = {}
        lm_dict = {lm[0]: (lm[1], lm[2]) for lm in landmarks}
        for name, idx in tip_ids.items():
            if idx in lm_dict:
                tips[name] = lm_dict[idx]
        return tips

    def get_fingers_up(self, landmarks):
        if len(landmarks) < 21:
            return [False] * 5
        lm = {l[0]: (l[1], l[2]) for l in landmarks}
        fingers = []
        if lm[4][0] < lm[3][0]:
            fingers.append(True)
        else:
            fingers.append(False)
        for tip_id, pip_id in [(8, 6), (12, 10), (16, 14), (20, 18)]:
            fingers.append(lm[tip_id][1] < lm[pip_id][1])
        return fingers

    def draw_landmarks(self, frame):
        """Draw landmarks AND store frame for the overlay preview."""
        if self.results and self.results.multi_hand_landmarks:
            for hand_lm in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_lm, self.mp_hands.HAND_CONNECTIONS
                )

        with self._frame_lock:
            self._latest_frame = frame.copy()

        return frame

    def get_preview_frame(self):
        """Thread-safe getter for the latest frame (for the UI overlay)."""
        with self._frame_lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def release(self):
        self.hands.close()