from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from statistics import mean

import numpy as np
from Pyfhel import PyCtxt
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server.app.main import app
from server.core.crypto.crypto_backends.ckks_pyfhel.context import generate_ckks_context
from server.core.model_registry.registry import MODEL_REGISTRY

RESULTS_DIR = ROOT / "benchmarks" / "results"

def _disable_rate_limits_for_benchmark() -> None:
    from server.app.routes import infer, infer_plain

    infer.enforce_infer_rate_limit = lambda tenant_id: None
    infer_plain.enforce_infer_rate_limit = lambda tenant_id: None

def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]

    rank = (p / 100.0) * (len(ordered) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)

    if low == high:
        return ordered[low]

    fraction = rank - low
    return ordered[low] * (1 - fraction) + ordered[high] * fraction


def _request_size_bytes(payload: dict) -> int:
    return len(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))


def _build_crypto_params(model_raw: dict) -> dict:
    encryption_parameters = model_raw["encryption_parameters"]
    return {
        "scheme": model_raw["he_scheme"],
        "poly_modulus_degree": encryption_parameters["poly_modulus_degree"],
        "coeff_modulus_bits": encryption_parameters["coeff_modulus_bits"],
        "scale": encryption_parameters["scale"],
    }


def _build_client_context(model_raw: dict):
    crypto_params = _build_crypto_params(model_raw)
    context = generate_ckks_context(crypto_params)
    context.keyGen()
    return context


def _encrypt_feature_vector(feature_vector: list[float], context) -> list[dict]:
    encrypted_inputs = []

    for value in feature_vector:
        pt = np.array([float(value)], dtype=np.float64)
        ct = context.encryptFrac(pt)
        encrypted_inputs.append(
            {
                "encoding": "hex",
                "payload": ct.to_bytes().hex(),
            }
        )

    return encrypted_inputs


def _decrypt_single_output(payload_hex: str, context) -> float:
    ct = PyCtxt(pyfhel=context, bytestring=bytes.fromhex(payload_hex))
    decrypted = context.decryptFrac(ct)

    if isinstance(decrypted, (list, tuple)):
        return float(decrypted[0])

    try:
        return float(decrypted)
    except TypeError:
        return float(decrypted[0])


def _extract_result_payload(job_body: dict) -> str:
    if "result" in job_body and isinstance(job_body["result"], dict):
        payload = job_body["result"].get("payload")
        if isinstance(payload, str):
            return payload

    if "payload" in job_body and isinstance(job_body["payload"], str):
        return job_body["payload"]

    if "job" in job_body and isinstance(job_body["job"], dict):
        result = job_body["job"].get("result", {})
        if isinstance(result, dict) and isinstance(result.get("payload"), str):
            return result["payload"]

    raise KeyError("Could not find encrypted result payload in jobs response")


def _run_plain_once(client: TestClient, model_id: str, version: str, feature_vector: list[float]) -> dict:
    payload = {
        "model_id": model_id,
        "version": version,
        "inputs": feature_vector,
    }

    started = time.perf_counter()
    response = client.post("/infer/plain", json=payload)
    ended = time.perf_counter()

    if response.status_code != 200:
        raise RuntimeError(f"Plain inference failed: {response.status_code} {response.text}")

    body = response.json()

    return {
        "latency_ms": (ended - started) * 1000.0,
        "request_size_bytes": _request_size_bytes(payload),
        "output": float(body["outputs"][0]),
    }


def _run_encrypted_once(
        client: TestClient,
        model_id: str,
        version: str,
        feature_vector: list[float],
        context,
) -> dict:
    encrypt_started = time.perf_counter()
    encrypted_inputs = _encrypt_feature_vector(feature_vector, context)
    encrypt_ended = time.perf_counter()

    request_payload = {
        "model_id": model_id,
        "version": version,
        "batch_size": 1,
        "inputs": encrypted_inputs,
    }

    infer_started = time.perf_counter()
    infer_response = client.post("/infer", json=request_payload)
    infer_ended = time.perf_counter()

    if infer_response.status_code != 200:
        raise RuntimeError(f"Encrypted inference failed: {infer_response.status_code} {infer_response.text}")

    job_id = infer_response.json()["job_id"]

    jobs_started = time.perf_counter()
    jobs_response = client.get(f"/jobs/{job_id}")
    jobs_ended = time.perf_counter()

    if jobs_response.status_code != 200:
        raise RuntimeError(f"Jobs fetch failed: {jobs_response.status_code} {jobs_response.text}")

    result_payload = _extract_result_payload(jobs_response.json())

    decrypt_started = time.perf_counter()
    output = _decrypt_single_output(result_payload, context)
    decrypt_ended = time.perf_counter()

    ciphertext_input_bytes = sum(len(bytes.fromhex(item["payload"])) for item in encrypted_inputs)
    ciphertext_output_bytes = len(bytes.fromhex(result_payload))

    encrypt_ms = (encrypt_ended - encrypt_started) * 1000.0
    infer_ms = (infer_ended - infer_started) * 1000.0
    jobs_ms = (jobs_ended - jobs_started) * 1000.0
    decrypt_ms = (decrypt_ended - decrypt_started) * 1000.0
    total_ms = encrypt_ms + infer_ms + jobs_ms + decrypt_ms

    return {
        "encrypt_ms": encrypt_ms,
        "infer_ms": infer_ms,
        "jobs_ms": jobs_ms,
        "decrypt_ms": decrypt_ms,
        "total_ms": total_ms,
        "request_size_bytes": _request_size_bytes(request_payload),
        "ciphertext_input_bytes": ciphertext_input_bytes,
        "ciphertext_output_bytes": ciphertext_output_bytes,
        "output": output,
    }


def _summarize(plain_runs: list[dict], encrypted_runs: list[dict]) -> dict:
    plain_latencies = [run["latency_ms"] for run in plain_runs]
    encrypted_totals = [run["total_ms"] for run in encrypted_runs]
    encrypted_encrypt = [run["encrypt_ms"] for run in encrypted_runs]
    encrypted_infer = [run["infer_ms"] for run in encrypted_runs]
    encrypted_jobs = [run["jobs_ms"] for run in encrypted_runs]
    encrypted_decrypt = [run["decrypt_ms"] for run in encrypted_runs]

    plain_request_sizes = [run["request_size_bytes"] for run in plain_runs]
    encrypted_request_sizes = [run["request_size_bytes"] for run in encrypted_runs]
    encrypted_input_bytes = [run["ciphertext_input_bytes"] for run in encrypted_runs]
    encrypted_output_bytes = [run["ciphertext_output_bytes"] for run in encrypted_runs]

    absolute_errors = [
        abs(plain_run["output"] - encrypted_run["output"])
        for plain_run, encrypted_run in zip(plain_runs, encrypted_runs)
    ]

    return {
        "plain": {
            "runs": len(plain_runs),
            "mean_latency_ms": mean(plain_latencies),
            "p50_latency_ms": _percentile(plain_latencies, 50),
            "p95_latency_ms": _percentile(plain_latencies, 95),
            "throughput_rps": len(plain_latencies) / (sum(plain_latencies) / 1000.0),
            "mean_request_size_bytes": mean(plain_request_sizes),
        },
        "encrypted": {
            "runs": len(encrypted_runs),
            "mean_total_latency_ms": mean(encrypted_totals),
            "p50_total_latency_ms": _percentile(encrypted_totals, 50),
            "p95_total_latency_ms": _percentile(encrypted_totals, 95),
            "throughput_rps": len(encrypted_totals) / (sum(encrypted_totals) / 1000.0),
            "mean_encrypt_ms": mean(encrypted_encrypt),
            "mean_infer_ms": mean(encrypted_infer),
            "mean_jobs_ms": mean(encrypted_jobs),
            "mean_decrypt_ms": mean(encrypted_decrypt),
            "mean_request_size_bytes": mean(encrypted_request_sizes),
            "mean_ciphertext_input_bytes": mean(encrypted_input_bytes),
            "mean_ciphertext_output_bytes": mean(encrypted_output_bytes),
        },
        "comparison": {
            "mean_abs_error": mean(absolute_errors),
            "max_abs_error": max(absolute_errors),
            "mean_request_expansion_ratio": mean(encrypted_request_sizes) / mean(plain_request_sizes),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark plaintext vs encrypted inference")
    parser.add_argument("--model-id", default="logistic_v1")
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--feature-value", type=float, default=0.1)
    args = parser.parse_args()

    model_key = (args.model_id, args.version)
    model_meta = MODEL_REGISTRY.get(model_key)
    if model_meta is None:
        raise KeyError(f"Unknown model/version: {model_key}")

    model_raw = model_meta.raw
    input_dimension = model_raw["inference"]["input_dimension"]
    feature_vector = [float(args.feature_value)] * input_dimension

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    _disable_rate_limits_for_benchmark()
    client = TestClient(app)
    context = _build_client_context(model_raw)

    print(f"Benchmarking model {args.model_id}@{args.version}")
    print(f"Input dimension: {input_dimension}")
    print(f"Warmup runs: {args.warmup}")
    print(f"Measured runs: {args.runs}")

    for _ in range(args.warmup):
        _run_plain_once(client, args.model_id, args.version, feature_vector)
        _run_encrypted_once(client, args.model_id, args.version, feature_vector, context)

    plain_runs = []
    encrypted_runs = []

    for i in range(args.runs):
        plain_result = _run_plain_once(client, args.model_id, args.version, feature_vector)
        encrypted_result = _run_encrypted_once(
            client,
            args.model_id,
            args.version,
            feature_vector,
            context,
        )

        plain_runs.append(plain_result)
        encrypted_runs.append(encrypted_result)

        print(
            f"[{i + 1}/{args.runs}] "
            f"plain={plain_result['latency_ms']:.2f} ms | "
            f"encrypted_total={encrypted_result['total_ms']:.2f} ms | "
            f"abs_error={abs(plain_result['output'] - encrypted_result['output']):.6f}"
        )

    summary = _summarize(plain_runs, encrypted_runs)

    raw_results = {
        "config": {
            "model_id": args.model_id,
            "version": args.version,
            "runs": args.runs,
            "warmup": args.warmup,
            "feature_value": args.feature_value,
            "input_dimension": input_dimension,
        },
        "plain_runs": plain_runs,
        "encrypted_runs": encrypted_runs,
        "summary": summary,
    }

    summary_path = RESULTS_DIR / "summary.json"
    runs_path = RESULTS_DIR / "runs.json"

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    runs_path.write_text(json.dumps(raw_results, indent=2), encoding="utf-8")

    print("\nSummary")
    print(json.dumps(summary, indent=2))
    print(f"\nWrote {summary_path}")
    print(f"Wrote {runs_path}")


if __name__ == "__main__":
    main()