from __future__ import annotations

from typing import List

from .api import API
from .discovery import Discovery
from .infer import Infer
from .jobs import Jobs
from .ckks.session import CKKS_Session
from .errors import SchemaValidationError


class Client:
    """
    High-level SDK interface for encrypted inference.

    values may be:
    - a single sample: List[float]
    - a batch of samples: List[List[float]]
    """

    def __init__(self, base_url: str, tenant_id: str | None = None):
        default_headers = {}
        if tenant_id:
            default_headers["X-Tenant-ID"] = tenant_id

        self.api = API(base_url, default_headers=default_headers)
        self.discovery = Discovery(self.api)
        self.infer_api = Infer(self.api)
        self.jobs = Jobs(self.api)

    def infer(
            self,
            model_id: str,
            values: List[float] | List[List[float]],
            version: str | None = None,
    ) -> list[float]:
        model = self.discovery.get_model(model_id)

        if version is None:
            version = model.get("version")

        if not version:
            raise SchemaValidationError(
                f"Model '{model_id}' is missing a usable version field",
                payload=model,
            )

        batch = self._normalize_batch(values)
        self._validate_inputs_against_model(model, batch)

        session = CKKS_Session.from_model(model)
        ciphertexts = session.encrypt_feature_batch(batch)

        job = self.infer_api.submit(
            model_id=model_id,
            version=version,
            batch_size=len(batch),
            inputs=ciphertexts,
        )

        response = self.jobs.wait(job["job_id"])
        return session.decrypt_slots(response, batch_size=len(batch))

    def _normalize_batch(
            self,
            values: List[float] | List[List[float]],
    ) -> List[List[float]]:
        if not isinstance(values, list) or len(values) == 0:
            raise SchemaValidationError(
                "values must be a non-empty list of floats or list of float vectors",
                payload={"values": values},
            )

        first = values[0]

        if isinstance(first, (int, float)):
            if not all(isinstance(x, (int, float)) for x in values):
                raise SchemaValidationError(
                    "Single input vector must contain only numeric values",
                    payload={"values": values},
                )
            return [list(values)]

        if isinstance(first, list):
            for vector in values:
                if not isinstance(vector, list):
                    raise SchemaValidationError(
                        "Batched inputs must be a list of vectors",
                        payload={"values": values},
                    )
                if len(vector) == 0:
                    raise SchemaValidationError(
                        "Input vectors must not be empty",
                        payload={"values": values},
                    )
                if not all(isinstance(x, (int, float)) for x in vector):
                    raise SchemaValidationError(
                        "Each input vector must contain only numeric values",
                        payload={"values": values},
                    )
            return values

        raise SchemaValidationError(
            "values must be a numeric vector or a batch of numeric vectors",
            payload={"values": values},
        )

    def _validate_inputs_against_model(
            self,
            model: dict,
            batch: List[List[float]],
    ) -> None:
        inference = model.get("inference", {})
        constraints = model.get("constraints", {})

        input_dimension = inference.get("input_dimension")
        max_batch_size = constraints.get("max_batch_size")

        if input_dimension is None:
            raise SchemaValidationError(
                "Model metadata missing inference.input_dimension",
                payload=model,
            )

        if not isinstance(input_dimension, int) or input_dimension < 1:
            raise SchemaValidationError(
                "Model inference.input_dimension must be a positive integer",
                payload=model,
            )

        if max_batch_size is not None:
            if not isinstance(max_batch_size, int) or max_batch_size < 1:
                raise SchemaValidationError(
                    "Model constraints.max_batch_size must be a positive integer",
                    payload=model,
                )

            if len(batch) > max_batch_size:
                raise SchemaValidationError(
                    f"Batch size {len(batch)} exceeds model max_batch_size {max_batch_size}",
                    payload={"batch_size": len(batch), "max_batch_size": max_batch_size},
                )

        for i, vector in enumerate(batch):
            if len(vector) != input_dimension:
                raise SchemaValidationError(
                    f"Input vector at batch index {i} has dimension {len(vector)}, "
                    f"expected {input_dimension}",
                    payload={
                        "batch_index": i,
                        "actual_dimension": len(vector),
                        "expected_dimension": input_dimension,
                    },
                )