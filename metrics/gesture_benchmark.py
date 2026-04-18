"""
Benchmarks gesture recognition accuracy, latency, and FPS.
Run this script, perform each gesture on camera when prompted,
and it will log detections with ground truth labels.
"""
import cv2
import time
import numpy as np
from collections import Counter
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
)
import matplotlib.pyplot as plt
import seaborn as sns

from hand_tracking.tracker import HandTracker
from hand_tracking.gesture_recognizer import GestureRecognizer
from config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT

GESTURES = ["move", "click", "right_click", "scroll"]
SAMPLES_PER_GESTURE = 30
SECONDS_PER_GESTURE = 8


def benchmark():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    tracker = HandTracker()
    recognizer = GestureRecognizer()

    y_true, y_pred = [], []
    latencies = []
    fps_list = []

    for gesture in GESTURES:
        print(f"\n>>> Perform '{gesture}' gesture for {SECONDS_PER_GESTURE}s")
        print("    Starting in 3 seconds...")
        time.sleep(3)

        samples = 0
        start = time.time()
        frame_count = 0

        while samples < SAMPLES_PER_GESTURE and \
              (time.time() - start) < SECONDS_PER_GESTURE:
            ret, frame = cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)

            t0 = time.time()
            tracker.process_frame(frame)
            landmarks = tracker.get_landmark_positions(frame)
            tips = tracker.get_finger_tips(landmarks)
            fingers_up = tracker.get_fingers_up(landmarks)
            result = recognizer.detect_gesture(tips, fingers_up)
            t1 = time.time()

            if landmarks:
                latencies.append((t1 - t0) * 1000)  # ms
                y_true.append(gesture)
                y_pred.append(result["action"])
                samples += 1

            frame_count += 1
            cv2.putText(
                frame, f"Do: {gesture} ({samples}/{SAMPLES_PER_GESTURE})",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
            )
            cv2.imshow("Benchmark", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        elapsed = time.time() - start
        if elapsed > 0:
            fps_list.append(frame_count / elapsed)

    cap.release()
    cv2.destroyAllWindows()
    tracker.release()

    report(y_true, y_pred, latencies, fps_list)


def report(y_true, y_pred, latencies, fps_list):
    print("\n" + "=" * 60)
    print("GESTURE RECOGNITION METRICS")
    print("=" * 60)
    print(f"Total samples: {len(y_true)}")
    print(f"Overall Accuracy: {accuracy_score(y_true, y_pred) * 100:.2f}%")
    print(f"\nPer-gesture classification report:")
    print(classification_report(y_true, y_pred, labels=GESTURES, zero_division=0))

    print(f"\nLatency (ms): mean={np.mean(latencies):.2f}, "
          f"median={np.median(latencies):.2f}, "
          f"p95={np.percentile(latencies, 95):.2f}")
    print(f"FPS: mean={np.mean(fps_list):.2f}")

    cm = confusion_matrix(y_true, y_pred, labels=GESTURES)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=GESTURES,
                yticklabels=GESTURES, cmap="Blues")
    plt.title("Gesture Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig("metrics/plots/gesture_confusion_matrix.png")
    plt.show()


if __name__ == "__main__":
    benchmark()