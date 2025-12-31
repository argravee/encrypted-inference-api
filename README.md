# Encrypted Inference API (v1)

A protocol and reference specification for privacy-preserving machine learning
inference using homomorphic encryption.

---

## Overview

This repository defines the **v1 protocol** for encrypted machine learning
inference. It specifies how clients discover supported models, encrypt inputs
locally, submit inference requests, and receive encrypted results without
exposing plaintext data or cryptographic secrets to the server.

The focus of this project is **protocol correctness, clarity, and adoptability**.

---

## Non-Goals

This repository does **not**:

- provide a production-ready server implementation
- perform model training or fine-tuning
- manage encryption keys or key distribution
- expose cryptographic internals or noise budgets
- guarantee numeric exactness of decrypted results

Approximation error is an expected property of homomorphic encryption and is not
considered a protocol failure.

---

## Repository Structure

- `docs/api.md`  
  Human-readable protocol specification, including API goals, invariants,
  error taxonomy, retry semantics, and versioning rules.

- `schemas/`  
  JSON Schemas defining the structural contracts for requests, responses,
  and error payloads.

- `openapi.yaml`  
  OpenAPI 3.1 specification that formally encodes the v1 protocol for tooling,
  validation, and SDK generation.

- `docs/api/examples/`  
  Example requests and responses for reference and testing.

---

## Status

The **v1 protocol specification is complete and frozen**.

A reference server implementation is planned as a subsequent phase and will
conform strictly to the published protocol, schemas, and OpenAPI definition.


---

## Versioning

The protocol follows semantic versioning at the API level.

Breaking changes will only occur in major versions.  
All `v1.x` releases preserve wire compatibility and error semantics.

---

## License

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License in the LICENSE file at the root of this repository.
