"""
Measures CPU, RAM, and end-to-end pipeline latency
of the hand tracking loop.
"""
import cv2
import time
import psutil
import os
import numpy as np
import matplotlib.pyplot as plt

from hand_tracking.tracker import HandTracker
from hand_tracking.gesture_recognizer import GestureRecognizer
from config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT

DURATION = 30 


def benchmark():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    tracker = HandTracker()
    recognizer = GestureRecognizer()
    process = psutil.Process(os.getpid())

    frame_times, cpu_samples, mem_samples = [], [], []
    stage_times = {"capture": [], "track": [], "recognize": []}

    start = time.time()
    while time.time() - start < DURATION:
        t_loop = time.perf_counter()

        t0 = time.perf_counter()
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        t1 = time.perf_counter()

        tracker.process_frame(frame)
        landmarks = tracker.get_landmark_positions(frame)
        tips = tracker.get_finger_tips(landmarks)
        fingers_up = tracker.get_fingers_up(landmarks)
        t2 = time.perf_counter()

        recognizer.detect_gesture(tips, fingers_up)
        t3 = time.perf_counter()

        stage_times["capture"].append((t1 - t0) * 1000)
        stage_times["track"].append((t2 - t1) * 1000)
        stage_times["recognize"].append((t3 - t2) * 1000)
        frame_times.append((t3 - t_loop) * 1000)

        cpu_samples.append(process.cpu_percent(interval=None))
        mem_samples.append(process.memory_info().rss / (1024 * 1024))

    cap.release()
    tracker.release()

    print("=" * 60)
    print("SYSTEM PERFORMANCE METRICS")
    print("=" * 60)
    fps = 1000 / np.mean(frame_times)
    print(f"Total frames: {len(frame_times)}")
    print(f"Average FPS: {fps:.2f}")
    print(f"\nPer-stage latency (ms):")
    for stage, vals in stage_times.items():
        print(f"  {stage:10s}: mean={np.mean(vals):.2f}, "
              f"p95={np.percentile(vals, 95):.2f}")
    print(f"\nEnd-to-end latency (ms): "
          f"mean={np.mean(frame_times):.2f}, "
          f"p95={np.percentile(frame_times, 95):.2f}")
    print(f"\nCPU usage: mean={np.mean(cpu_samples):.2f}%")
    print(f"RAM usage: mean={np.mean(mem_samples):.2f} MB, "
          f"peak={np.max(mem_samples):.2f} MB")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    axes[0].plot(frame_times)
    axes[0].set_title("Frame Latency (ms)")
    axes[0].set_xlabel("Frame")
    axes[1].plot(cpu_samples, color="orange")
    axes[1].set_title("CPU Usage (%)")
    axes[2].plot(mem_samples, color="green")
    axes[2].set_title("Memory Usage (MB)")
    plt.tight_layout()
    plt.savefig("metrics/plots/system_performance.png")
    plt.show()


if __name__ == "__main__":
    benchmark()