# Encrypted Inference API (v1)

A protocol and reference specification for privacy-preserving machine learning
inference using homomorphic encryption.



## Overview

This repository defines the **v1 protocol** for encrypted machine learning
inference. It specifies how clients discover supported models, encrypt inputs
locally, submit inference requests, and receive encrypted results without
exposing plaintext data or cryptographic secrets to the server.

The focus of this project is **protocol correctness, clarity, and adoptability**.

### Intended Audience

This specification is intended for:

- Engineers building privacy-preserving ML systems
- Researchers evaluating encrypted inference protocols
- Teams implementing compatible clients, servers, or SDKs


## Non-Goals

This repository does **not**:

- provide a production-ready server implementation
- perform model training or fine-tuning
- manage encryption keys or key distribution
- expose cryptographic internals or noise budgets
- guarantee numeric exactness of decrypted results

Approximation error is an inherent property of approximate homomorphic encryption schemes and is not
considered a protocol failure.


## Status

The v1 protocol specification is defined and partially stabilized, with a working reference backend focused on cryptographic correctness and validation semantics.

Core protocol artifacts are present:

- JSON Schemas and OpenAPI definition for v1 payloads and error shapes
- A CKKS (Pyfhel) reference backend implementing context management, 
ciphertext deserialization, context compatibility enforcement, and scale sanity checks
- End-to-end automated tests demonstrating a real CKKS round-trip: encrypt → serialize → server-side validate → decrypt

The reference backend is a conformance target for the protocol and validation rules, 
not a production-ready system. The protocol may still change prior to a formal 
v1.0 freeze, but current work prioritizes wire stability and tightening 
validation rather than adding new endpoints.

### What Remains

- Harden CKKS validation against malformed and adversarial ciphertext inputs
- Expand negative and adversarial end-to-end tests (schema violations, scale mismatches, incompatible contexts)
- Formalize and verify conformance between JSON Schemas, OpenAPI definitions, and runtime validation behavior



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
- `server/`
  Reference implementation focusing on correctness and validation semantics
- `docs/api/examples/`  
  Example requests and responses for reference and testing.
- `tests/`
  End-to-end tests validating encrypted ciphertext handling.

## High-Level Flow

1. Client queries `/models` to discover supported encrypted models
2. Client encrypts inputs locally using model requirements
3. Client submits encrypted inference request
4. Server validates ciphertext structure and compatibility
5. Server performs homomorphic evaluation
6. Encrypted result is returned to the client
7. Client decrypts result locally

## Reference Implementation 

A reference server implementation is
included to validate protocol correctness and cryptographic handling.

The implementation prioritizes:
- strict validation before inference
- deterministic cryptographic context usage
- safe rejection of malformed or incompatible ciphertexts
- It is not intended to be production-ready, but serves as a correctness 
and integration reference.


## Versioning

The protocol follows semantic versioning at the API level.

Breaking changes will only occur in major versions.  
All `v1.x` releases preserve wire compatibility and error semantics. Further details can be
found at `docs/architecture/versioning.md`



## Conformance

An implementation is considered v1-compliant if it:

- Accepts and produces payloads conforming to the published JSON Schemas
- Implements all required endpoints defined in `openapi.yaml`
- Preserves documented error semantics and retry guarantees
- Does not weaken validation requirements
Behavior outside the protocol (logging, scheduling, execution strategy) is implementation-defined.

Unless explicitly stated otherwise, only protocol artifacts
(JSON Schemas, OpenAPI definitions, and documented invariants)
are considered normative. Reference backend behavior outside
these contracts is non-normative and may change without
constituting a protocol revision.




## License

Licensed under the Apache License, Version 2.0.
