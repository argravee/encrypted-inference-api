# Protocol Versioning and Compatibility
## 1. Purpose 
This document defines the versioning model and compatibility guarantees for the 
Encrypted Inference API protocol.

This document applies to all protocol surfaces, including:

- HTTP endpoints
- request and response schemas
- error semantics
- validation rules

## 2. Versioning Model
The protocol follows Semantic Versioning at the API / wire level:
- MAJOR.MINOR.PATCH

Where:
- MAJOR versions introduce breaking changes
- MINOR versions introduce backward-compatible additions
- PATCH versions introduce backward-compatible fixes or clarifications

The current protocol version is v1.0.0.

## 3. What is versioned
The following components are versioned together:

- HTTP endpoint contracts
- JSON request and response schemas
- Validation behavior and invariants
- Error codes and error semantics
- Required and optional fields
- Interpretation of existing fields
- Internal implementation details (e.g. queue backend, cryptographic library choice)
are not part of the protocol version.

## 4. Where Version Appears
### 4.1 Response Versioning
All protocol responses must include an explicit version field

This allows clients to:
- confirm compatibility 
- detect server upgrades
- enforce strict parsing rules

### 4.2 Request Versioning
Requests may include it as a field for forward compatibility.

If present:
- the server must validate the requested version
- unsupported versions must be rejected
If absent:
- the server assumes the current major version

## 5. Compatibility Guarantees
### 5.1 v1.x Compatibility Rules

All v1.x releases guarantee wire compatibility.

Specifically:
- Existing fields will not be removed or redefined
- Existing error codes will not change meaning
- Validation rules will not become stricter in ways that reject previously valid requests
- Response semantics remain stable

The following are allowed in v1.x:
- new optional fields
- new endpoints
- additional error codes
- relaxed validation rules
- documentation clarifications

### 5.2 Breaking Changes (v2+)

Breaking changes are only permitted in a new major version.

Examples of breaking changes:
- removing or renaming fields
- changing field meaning or units
- altering validation behavior that rejects previously valid inputs
- changing error semantics
- modifying cryptographic assumptions
- Clients must explicitly opt into a new major version.

## 6. Server Behavior on Version Mismatch
### 6.1 Unsupported Version

If a client requests an unsupported protocol version, the server must reject the request.

The server returns:
- HTTP 400 Bad Request or 409 Conflict
- a structured error with code UNSUPPORTED_API_VERSION

### 6.2 Missing Version

If a request omits api_version:

- the server assumes the current major version
- behavior must be identical to explicitly requesting that version

## 7. Deprecation Policy

Within a major version:

- fields may be marked as deprecated
- deprecated fields remain supported for the entire major version
- removal of deprecated fields only occurs in the next major version

Deprecation notices are documented but never silently enforced.

## 8. Relationship to Schemas and OpenAPI

- JSON Schemas encode the versioned structure of requests and responses
- The OpenAPI specification corresponds to a specific protocol version
- Schema changes that affect wire compatibility require a major version bump
- Schemas are considered normative for validation behavior.

## 9. Non-Goals

This versioning model does not attempt to:

- provide automatic version negotiation
- support mixed-version requests within a single session
- guarantee compatibility across major versions
- Clients and servers must explicitly agree on the protocol version.