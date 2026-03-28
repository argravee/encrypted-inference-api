from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "benchmarks" / "results" / "summary.json"
DOCS_ASSETS_DIR = ROOT / "docs" / "assets"


def _load_summary() -> dict:
    with SUMMARY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_plot(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()


def make_latency_chart(summary: dict) -> None:
    plain = summary["plain"]
    encrypted = summary["encrypted"]

    labels = ["Mean", "P50", "P95"]
    plain_values = [
        plain["mean_latency_ms"],
        plain["p50_latency_ms"],
        plain["p95_latency_ms"],
    ]
    encrypted_values = [
        encrypted["mean_total_latency_ms"],
        encrypted["p50_total_latency_ms"],
        encrypted["p95_total_latency_ms"],
    ]

    x = range(len(labels))
    width = 0.35

    plt.figure(figsize=(8, 5))
    plt.bar([i - width / 2 for i in x], plain_values, width=width, label="Plaintext")
    plt.bar([i + width / 2 for i in x], encrypted_values, width=width, label="Encrypted")

    plt.xticks(list(x), labels)
    plt.ylabel("Latency (ms)")
    plt.title("Plaintext vs Encrypted Inference Latency")
    plt.legend()

    _save_plot(DOCS_ASSETS_DIR / "benchmark_latency.png")


def make_request_size_chart(summary: dict) -> None:
    plain_size = summary["plain"]["mean_request_size_bytes"]
    encrypted_size = summary["encrypted"]["mean_request_size_bytes"]

    labels = ["Plaintext", "Encrypted"]
    values = [plain_size, encrypted_size]

    plt.figure(figsize=(7, 5))
    bars = plt.bar(labels, values)

    plt.yscale("log")
    plt.ylabel("Request Size (bytes, log scale)")
    plt.title("Request Size Comparison")

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            f"{value:,.0f} B",
            ha="center",
            va="bottom",
            )

    _save_plot(DOCS_ASSETS_DIR / "benchmark_request_size.png")


def make_encrypted_breakdown_chart(summary: dict) -> None:
    encrypted = summary["encrypted"]

    labels = ["Encrypt", "Infer", "Jobs Fetch", "Decrypt"]
    values = [
        encrypted["mean_encrypt_ms"],
        encrypted["mean_infer_ms"],
        encrypted["mean_jobs_ms"],
        encrypted["mean_decrypt_ms"],
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)
    plt.ylabel("Time (ms)")
    plt.title("Encrypted End-to-End Timing Breakdown")

    _save_plot(DOCS_ASSETS_DIR / "benchmark_encrypted_breakdown.png")


def main() -> None:
    summary = _load_summary()

    make_latency_chart(summary)
    make_request_size_chart(summary)
    make_encrypted_breakdown_chart(summary)

    print("Wrote:")
    print(DOCS_ASSETS_DIR / "benchmark_latency.png")
    print(DOCS_ASSETS_DIR / "benchmark_request_size.png")
    print(DOCS_ASSETS_DIR / "benchmark_encrypted_breakdown.png")


if __name__ == "__main__":
    main()