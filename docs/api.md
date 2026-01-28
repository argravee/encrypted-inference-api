# Encrypted Inference API


This document defines the **v1 protocol-level API** for privacy-preserving
machine learning inference using CKKS homomorphic encryption.

## API Overview

This API exposes a minimal set of endpoints required to:
- discover available encrypted models
- submit encrypted inference requests
- validate operational health
- ensure protocol compatibility

## GET /models

### Purpose
Returns the lsit of encrypted models supported by the server along with their **cryptographic and inference requirements**.

Clients must call this endpoint before encrypting inputs in order to:

- select a valid model_id

- configure encryption parameters correctly

- ensure ciphertext compatibility
### Response Body
a JSON object containing:
- api_version
- models[]

### Guarantees
- Model registry is validated at startup
- Response is stable during server lifetime

### Errors
- 500 Internal Server Error on registry validation error or unexpected server error.
---


## POST /infer
### Purpose
Submits an encrypted inference request for async execution.

The server never decrypts inputs, all ciphertexts are validated strucutually and cryptogrpahically 
before being accepted.

### Request Body
A JSON object containing:
- model_id
- version
- inputs[]

Each input contains:
- encoding
- payload (encoded ciphertext bytes)

Formal request schema is outlined in infer.request.schema.json
### Response Body 
On success server returns:
- job_id
- status (accepted)

### Async Semantics
- Requests are validated synchronously
- Valid requests are enqueued for background processing 
- Inference execution occurs outside the request lifecycle
### Validation rules
Requests are rejected if any of the following fail:
1. Envelope structure validation
2. Payload size limits
3. Ciphertext deserialization
4. Cryptographic scheme compatibility
5. Context and parameter compatibility
6. Model-specific constraints

Jobs must pass all validation layers to be enqueued.
### Errors
- 400 Bad Request
- 404 Not found
- 409 Conflict
- 413 Payload Too Large
- 503 Service Unavailable 

## GET /jobs{job_id}
### Purpose
Retrieves the current status and result of an inference job.

### Response Body

A JSON object containing:
- job_id
- status (queued, running, done, failed)
- timestamps 
- encrypted result payload (if done)
- error message (if failed)

The encrypted result payload conforms to the response schema defined in
infer.response.schema.json

### Guarantees

- Job state transitions are monotonic.
- Results are immutable once produced.

### Errors
404 Not Found — unknown job_id

## GET /health
### Purpose
Provides a lightweight health check for operational monitoring.

### Response Body
- status: "ok"

### Guarantees
- Does not depend on model registry or job queue state.
- Safe to call frequently.

## /keys
### Purpose

Exposes the public cryptographic material required for clients to encrypt inputs 
compatible with the server.

Key material is:
- public-only
- scoped to protocol and model requirements
- never includes private or secret keys

### Response Body

Returns the minimal key set required for client-side encryption under
the declared model constraints.

### Guarantees

- Keys are consistent with the active cryptographic context.
- Keys are stable for the lifetime of the server process.

### Errors

- 503 Service Unavailable — cryptographic context not initialized

### Error Semantics

All error responses are:
- explicit
- deterministic
- machine-parseable
- Errors do not leak cryptographic secrets, plaintext data, or internal server state.

### Versioning

The API follows semantic versioning at the protocol level.
- Breaking changes only occur in major versions.
- All v1.x releases preserve wire compatibility and error semantics.