from functools import lru_cache
import json
from pathlib import Path

from jsonschema import validate


@lru_cache(maxsize=1)
def _load_infer_request_schema() -> dict:
    schema_path = (
            Path(__file__).resolve().parents[3]
            / "schemas"
            / "infer.request.schema.json"
    )

    with schema_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_envelope(envelope: dict) -> None:
    if not isinstance(envelope, dict):
        raise ValueError("Infer request body must be a JSON object")

    validate(instance=envelope, schema=_load_infer_request_schema())