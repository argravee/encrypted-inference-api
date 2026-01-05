

# Model Registry Architecture and Validation

## 1. Purpose

The model registry defines the **complete and authoritative set of encrypted models** supported by the server.

It specifies the cryptographic requirements, inference constraints, and compatibility guarantees that clients must rely on in order to correctly encrypt inputs and interpret results.

The registry is **protocol-critical**. Incorrect or ambiguous registry data can lead to failed inference, incorrect encryption, or undefined client behavior.

---

## 2. Registry Scope and Ownership

The model registry:

* Is loaded **once at server startup**
* Is **read-only for the lifetime of the process**
* Is owned and maintained by the **server operator**
* Is **not user-modifiable**
* Is the sole source of truth for `GET /models`

The registry does **not** support:

* Runtime mutation
* Partial availability
* Hot reloading
* Best-effort or degraded operation

Clients must assume that all registry data exposed by the server is **complete, internally consistent, and stable** for the duration of the server process.

---

## 3. Startup Validation Invariant

Registry validation is a **precondition for server startup**.

Before the server begins accepting requests:

* Every registry entry **must be validated**
* All required fields **must be present**
* All declared constraints **must be coherent**
* All protocol requirements **must be satisfied**

If **any** registry entry fails validation:

* The server **must refuse to start**
* Partial registry loading is **forbidden**
* Silent failure is **unacceptable**

This invariant ensures deterministic server behavior and protects clients from undefined or inconsistent protocol state.

---
## 4. Registry Immutability Invariant

Once the model registry has been successfully loaded and validated at startup, it becomes **immutable** for the lifetime of the server process.

Specifically:

* Registry contents **must not change** after startup
* Registry files **must not be reloaded** per request
* Registry entries **must not be mutated** at runtime
* No dynamic registration, removal, or modification is permitted

All requests handled by the server must observe the **same registry state** until the process is restarted.

---

### Rationale

Freezing the registry after startup guarantees:

* Deterministic server behavior
* Stable client expectations
* Elimination of time-of-check / time-of-use inconsistencies
* Clear operational semantics for versioning and compatibility

Clients rely on registry data to correctly encrypt inputs and interpret outputs. Allowing registry mutation during runtime would invalidate these assumptions.

---

### Enforcement Model

Registry immutability is enforced as a **runtime invariant**:

* The registry is constructed once during startup
* The in-memory registry representation is treated as read-only
* All API endpoints reference the same frozen registry instance

Runtime behavior must not depend on external registry files or mutable state.

---

### Non-Goals

The registry immutability invariant explicitly does **not** support:

* Hot reloading of models
* Live configuration changes
* Partial or rolling registry updates
* Per-request registry recomputation

All registry changes require a **full server restart**.

---
## 5. Validation Layers

Registry validation is performed in **two distinct layers**: structural and semantic.

### 5.1 Schema Validation

Schema validation ensures that each registry file:

* Is valid JSON
* Conforms exactly to the published schema
* Includes all required fields
* Uses correct data types
* Uses only allowed field names
* Uses valid enumerated values where applicable

Schema validation is **strict**. Unknown or extraneous fields are rejected.

Passing schema validation guarantees **structural correctness**, but does not guarantee that the model description is executable or coherent.

---

### 5.2 Semantic Validation

Semantic validation ensures that a registry entry is **internally consistent and protocol-valid**.

Semantic validation rejects registry entries that, while structurally valid, contain **obvious inconsistencies** or impossible configurations.

Examples include (non-exhaustive):

* Declared cryptographic schemes not supported by the protocol
* Contradictory constraints (e.g., incompatible dimensions or limits)
* Parameter combinations that cannot be executed under the declared scheme
* Unsupported or undefined protocol features
* Version declarations that violate compatibility rules

Semantic validation ensures that each model entry represents a **coherent, executable contract** under the protocol.

---

## 6. Rejection Conditions

Any of the following conditions **must cause startup failure**:

* JSON parsing errors
* Schema violations
* Missing required fields
* Invalid enum values
* Unsupported protocol versions
* Semantic inconsistencies
* Ambiguous or contradictory constraints

All validation failures are considered **fatal**.

---

## 7. Failure Semantics

When registry validation fails:

* The server must **terminate startup**
* The failure must be **explicit**
* The failure must be **actionable**

At minimum, validation failures must identify:

* The registry file that failed
* The category of failure (schema or semantic)
* The specific constraint or field involved

The server must not:

* Attempt to repair invalid entries
* Substitute defaults
* Skip invalid models
* Continue with a partially loaded registry

---

## 8. Non-Goals

The registry validation system does **not** attempt to:

* Infer missing information
* Normalize or auto-correct values
* Provide backward compatibility for invalid entries
* Support dynamic model registration
* Perform runtime re-validation

All registry entries are expected to be **explicit, correct, and intentional**.

---

## 9. Relationship to API Endpoints

The `GET /models` endpoint reflects the **validated and frozen registry**.

Clients may assume that:

* All returned models are valid under the protocol
* All declared constraints are enforceable
* Registry data will not change during the session

No per-request validation of registry contents occurs at runtime.


