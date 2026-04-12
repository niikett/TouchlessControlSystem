import math
import time


def distance(p1, p2):
    """Euclidean distance between two (x,y) points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


class GestureRecognizer:
    """Classify hand gestures from landmark data."""

    def __init__(self, pinch_threshold=40, scroll_speed=120):
        self.pinch_threshold = pinch_threshold
        self.scroll_speed = scroll_speed

        self.click_cooldown = 0.5
        self.last_click_time = 0
        self.last_right_click_time = 0

        self.prev_scroll_y = None
        self.scroll_accumulator = 0
        self.scroll_threshold = 3  
        
    def detect_gesture(self, finger_tips, fingers_up):
        """
        Detect gesture. Cursor ALWAYS follows index finger.

        Priority:
        1. Scroll (index + middle up only)
        2. Click (thumb + index pinch)
        3. Right Click (thumb + middle pinch, index down)
        4. Move (default - always)
        """
        if not finger_tips or not fingers_up or len(fingers_up) < 5:
            self.prev_scroll_y = None
            self.scroll_accumulator = 0
            return {
                "action": "none",
                "position": None,
                "scroll_delta": None,
            }

        result = {
            "action": "move",
            "position": finger_tips.get("index"),
            "scroll_delta": None,
        }

        thumb_up, index_up, middle_up, ring_up, pinky_up = fingers_up

        index_pos = finger_tips.get("index")
        thumb_pos = finger_tips.get("thumb")
        middle_pos = finger_tips.get("middle")

        now = time.time()

        if (
            index_up
            and middle_up
            and not ring_up
            and not pinky_up
            and index_pos
        ):
            scroll_y = index_pos[1]
            if middle_pos:
                scroll_y = (index_pos[1] + middle_pos[1]) / 2

            if self.prev_scroll_y is not None:
                raw_delta = self.prev_scroll_y - scroll_y
                self.scroll_accumulator += raw_delta

                if abs(self.scroll_accumulator) > self.scroll_threshold:
        
                    direction = (
                        1
                        if self.scroll_accumulator > 0
                        else -1
                    )
                    magnitude = min(
                        abs(self.scroll_accumulator) / 1.5,
                        self.scroll_speed,
                    )
                    scroll_amount = int(direction * max(magnitude, 5))

                    self.scroll_accumulator = 0
                    self.prev_scroll_y = scroll_y
                    return {
                        "action": "scroll",
                        "position": index_pos,
                        "scroll_delta": scroll_amount,
                    }

            self.prev_scroll_y = scroll_y
        
            return {
                "action": "scroll",
                "position": index_pos,
                "scroll_delta": 0,
            }

        self.prev_scroll_y = None
        self.scroll_accumulator = 0

        if index_pos and thumb_pos:
            dist = distance(index_pos, thumb_pos)
            if dist < self.pinch_threshold:
                if now - self.last_click_time > self.click_cooldown:
                    self.last_click_time = now
                    result["action"] = "click"
                    return result

        if (
            middle_pos
            and thumb_pos
            and middle_up
            and not index_up
        ):
            dist = distance(middle_pos, thumb_pos)
            if dist < self.pinch_threshold:
                if (
                    now - self.last_right_click_time
                    > self.click_cooldown
                ):
                    self.last_right_click_time = now
                    result["action"] = "right_click"
                    return result

        result["action"] = "move"
        return result