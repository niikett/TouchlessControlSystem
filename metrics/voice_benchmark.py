"""
Benchmarks the CommandParser against ground truth.
Calculates parsing accuracy, precision, recall, F1, and latency.
"""
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
)

from voice.command_parser import CommandParser
from metrics.test_data.voice_test_cases import TEST_CASES


def benchmark():
    parser = CommandParser()

    y_true_cat, y_pred_cat = [], []
    y_true_act, y_pred_act = [], []
    latencies = []
    correct_both = 0

    for text, exp_cat, exp_act in TEST_CASES:
        t0 = time.perf_counter()
        parsed = parser.parse(text)
        t1 = time.perf_counter()

        latencies.append((t1 - t0) * 1000)
        y_true_cat.append(exp_cat)
        y_pred_cat.append(parsed.category)
        y_true_act.append(exp_act)
        y_pred_act.append(parsed.action)

        match = (parsed.category == exp_cat and parsed.action == exp_act)
        if match:
            correct_both += 1

        status = "✅" if match else "❌"
        print(f"{status} '{text}' → {parsed.category}/{parsed.action} "
              f"(expected {exp_cat}/{exp_act})")

    print("\n" + "=" * 60)
    print("VOICE COMMAND PARSER METRICS")
    print("=" * 60)
    total = len(TEST_CASES)
    print(f"Total test cases: {total}")
    print(f"Full match (category + action): "
          f"{correct_both}/{total} = {correct_both / total * 100:.2f}%")
    print(f"Category accuracy: "
          f"{accuracy_score(y_true_cat, y_pred_cat) * 100:.2f}%")
    print(f"Action accuracy:   "
          f"{accuracy_score(y_true_act, y_pred_act) * 100:.2f}%")

    print(f"\nParse latency (ms): "
          f"mean={np.mean(latencies):.3f}, "
          f"max={np.max(latencies):.3f}")

    print("\n--- Category Classification Report ---")
    print(classification_report(y_true_cat, y_pred_cat, zero_division=0))

    labels = sorted(set(y_true_cat) | set(y_pred_cat))
    cm = confusion_matrix(y_true_cat, y_pred_cat, labels=labels)
    plt.figure(figsize=(10, 7))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels,
                yticklabels=labels, cmap="Greens")
    plt.title("Voice Command Category Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig("metrics/plots/voice_confusion_matrix.png")
    plt.show()


if __name__ == "__main__":
    benchmark()