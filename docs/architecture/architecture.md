# Architecture

This document describes the structure of the Encrypted Inference API reference implementation and the movement of data across the client, protocol layer, and server.

## System Summary

The system has two major sides:

- **Client / SDK**
- **Server / Reference Backend**

The client discovers model metadata, constructs a compatible CKKS session locally, encrypts inputs, submits ciphertexts, retrieves encrypted results, and decrypts them locally.

The server exposes the protocol routes, validates request envelopes, validates ciphertext compatibility, performs homomorphic evaluation, and stores encrypted results in job state.

## Primary Design Principle

The protocol is designed so that:

- plaintext inputs remain client-side
- decryption capability remains client-side
- the server handles ciphertexts, metadata, and protocol validation
- protocol artifacts define the wire contract
- backend-specific cryptographic logic remains behind a backend abstraction

## Architecture Diagram

```mermaid
flowchart LR

    subgraph CLIENT["Client / SDK"]
        direction TB
        C1["Discovery Client<br/>GET /models"]
        C2["Model Metadata"]
        C3["CKKS Session Builder"]
        C4["Local Encryption"]
        C5["Inference Submitter<br/>POST /infer"]
        C6["Jobs Client<br/>GET /jobs/{id}"]
        C7["Local Decryption"]
    end

    subgraph SERVER["Server / Reference Backend"]
        direction TB
        S1["/models Route"]
        S2["/infer Route"]
        S3["/jobs/{id} Route"]
        S4["Model Registry"]
        S5["Envelope Validation"]
        S6["Ciphertext Validation"]
        S7["CKKS Backend"]
        S8["HE Execution"]
        S9["Job Store"]
    end

    C1 --> S1
    S1 --> S4
    S4 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5

    C5 --> S2
    S2 --> S5
    S5 --> S4
    S5 --> S6
    S6 --> S7
    S7 --> S8
    S8 --> S9

    C6 --> S3
    S3 --> S9
    S9 --> C7
```

## Request Lifecycle

A typical request follows this sequence:

1. The client calls `/models` to discover supported models and encryption requirements.
2. The client constructs a compatible CKKS session locally.
3. The client encrypts input features locally.
4. The client submits a ciphertext-bearing request to `/infer`.
5. The server validates the envelope and resolves the referenced model metadata.
6. The server validates ciphertext structure and compatibility through the crypto backend.
7. The server performs homomorphic evaluation.
8. The encrypted result is stored in job state.
9. The client retrieves the result through `/jobs/{id}` and decrypts it locally.

## Notes

This diagram is implementation-oriented. It is intended to help contributors understand the reference backend quickly, not to replace the normative protocol artifacts.

The protocol contract remains defined by the schemas, OpenAPI description, and documented invariants.
