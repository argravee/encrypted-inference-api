from json import JSONDecodeError
from pathlib import Path
import json
import jsonschema
from typing import Any

from pydantic import ValidationError

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = Path(__file__).resolve().parent / "model_registry_entry.schema.json"

if not SCHEMA_PATH.exists():
    raise RuntimeError(f"Schema file not found: {SCHEMA_PATH}")

if not SCHEMA_PATH.is_file():
    raise RuntimeError(f"Schema path is not a file: {SCHEMA_PATH}")

try:
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        MODEL_REGISTRY_SCHEMA = json.load(f)
except JSONDecodeError as e:
    raise RuntimeError(
        f"Invalid JSON in schema file {SCHEMA_PATH}: {e}"
    ) from e

if not isinstance(MODEL_REGISTRY_SCHEMA, dict):
    raise RuntimeError(
        f"Schema root must be a JSON object: {SCHEMA_PATH}"
    )
def validate_model_registry_entry(entry: dict[str,Any])->None:
    jsonschema.validate(instance=entry, schema=MODEL_REGISTRY_SCHEMA)

    return None
