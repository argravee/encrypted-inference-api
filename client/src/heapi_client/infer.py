from __future__ import annotations

from typing import Any

from .api import API
from .errors import SchemaValidationError


class Infer:
    def __init__(self, api: API) -> None:
        self.api = api

    def submit(
            self,
            model_id: str,
            version: str,
            batch_size: int,
            inputs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not model_id:
            raise SchemaValidationError("model_id is required")
        if not version:
            raise SchemaValidationError("version is required")
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise SchemaValidationError("batch_size must be a positive integer")
        if not isinstance(inputs, list) or not inputs:
            raise SchemaValidationError("inputs must be a non-empty list")

        payload = {
            "model_id": model_id,
            "version": version,
            "batch_size": batch_size,
            "inputs": inputs,
        }

        return self.api.post("/infer", json=payload)

    def get_job(self, job_id: str) -> dict[str, Any]:
        if not job_id:
            raise SchemaValidationError("job_id is required")

        return self.api.get(f"/jobs/{job_id}")