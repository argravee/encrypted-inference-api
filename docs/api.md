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

This endpoint should be called before attempting inference in order to encrypt inputs correctly and validate compatibility

### Request Body
None.

---
### Response Body

A JSON object containing an array of mode descriptors.

Each model descriptor includes:
- model identifier and version
- input and output dimensions
- required homomorphic encryption scheme
- required scale and depth
- supported activation type