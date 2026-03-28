# Benchmarking: Plaintext vs Encrypted Inference

## Overview

This document reports benchmarking methodology for the reference `logistic_v1` model served through two execution paths:

- **Plaintext baseline** via `POST /infer/plain`
- **Encrypted inference** via `POST /infer` using **CKKS / Pyfhel**

The goal is to quantify the **privacy-performance tradeoff** of homomorphic encrypted inference relative to a standard plaintext baseline.

## Benchmark Configuration

- **Model**: `logistic_v1`
- **Version**: `1.0.0`
- **Input dimension**: `8`
- **Warmup runs**: `3`
- **Measured runs**: `20`
- **Feature value**: `0.1` repeated across all input dimensions

## What Was Measured

### Plaintext path
For each plaintext run, the benchmark measured:

- end-to-end request latency for `POST /infer/plain`
- request size in bytes
- output value

### Encrypted path
For each encrypted run, the benchmark measured:

- client-side encryption time
- `POST /infer` request latency
- `/jobs/{id}` fetch latency
- client-side decryption time
- total client-observed end-to-end latency
- encrypted request size in bytes
- ciphertext input size in bytes
- ciphertext output size in bytes
- decrypted output value

### Comparison metrics
The benchmark also computed:

- mean absolute error between plaintext and decrypted encrypted outputs
- max absolute error
- request expansion ratio between encrypted and plaintext requests


## Reproducing

Run from the repo root:

```bash
python benchmarks/benchmark_inference.py --model-id logistic_v1 --version 1.0.0 --runs 20 --warmup 3