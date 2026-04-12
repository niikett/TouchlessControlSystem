import pyautogui
import numpy as np
from config import (
    SCREEN_W,
    SCREEN_H,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    SMOOTHING_FACTOR,
)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0


class CursorController:
    """Translate hand positions to screen cursor actions."""

    def __init__(self):
        self.prev_positions = []

    def _map_to_screen(self, hand_x, hand_y):
        """Map camera coordinates to screen coordinates."""
        x_min = int(CAMERA_WIDTH * 0.1)
        x_max = int(CAMERA_WIDTH * 0.9)
        y_min = int(CAMERA_HEIGHT * 0.1)
        y_max = int(CAMERA_HEIGHT * 0.9)

        hand_x = max(x_min, min(hand_x, x_max))
        hand_y = max(y_min, min(hand_y, y_max))

        screen_x = np.interp(hand_x, [x_min, x_max], [0, SCREEN_W])
        screen_y = np.interp(hand_y, [y_min, y_max], [0, SCREEN_H])

        return int(screen_x), int(screen_y)

    def _smooth(self, x, y):
        """Apply moving average smoothing to reduce jitter."""
        self.prev_positions.append((x, y))
        if len(self.prev_positions) > SMOOTHING_FACTOR:
            self.prev_positions.pop(0)

        avg_x = int(
            sum(p[0] for p in self.prev_positions)
            / len(self.prev_positions)
        )
        avg_y = int(
            sum(p[1] for p in self.prev_positions)
            / len(self.prev_positions)
        )
        return avg_x, avg_y

    def execute(self, gesture):
        """Execute cursor action based on gesture."""
        action = gesture["action"]
        position = gesture["position"]

        if action == "none" or position is None:
            return

        if action == "scroll":
            delta = gesture.get("scroll_delta", 0)
            if delta != 0:
                pyautogui.scroll(delta, _pause=False)
                print(f"  >> SCROLL delta={delta}")
            return

        screen_x, screen_y = self._map_to_screen(
            position[0], position[1]
        )
        smooth_x, smooth_y = self._smooth(screen_x, screen_y)

        smooth_x = max(0, min(smooth_x, SCREEN_W - 1))
        smooth_y = max(0, min(smooth_y, SCREEN_H - 1))

        if action == "move":
            pyautogui.moveTo(smooth_x, smooth_y, _pause=False)

        elif action == "click":
            pyautogui.click(smooth_x, smooth_y, _pause=False)
            print(f"  >> CLICK at ({smooth_x}, {smooth_y})")

        elif action == "right_click":
            pyautogui.rightClick(smooth_x, smooth_y, _pause=False)
            print(f"  >> RIGHT CLICK at ({smooth_x}, {smooth_y})")