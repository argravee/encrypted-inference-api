from pathlib import Path
import json
from dataclasses import dataclass
from typing import Dict, Any, List
#TODO: Invoke schema validation on each parsed registry JSON before extracting fields
#TODO: Invoke semantic validation on each schema-valid registry JSON
#TODO: Enforce validation order: JSON parse → schema validation → semantic validation → registry-wide checks
#TODO: Convert all validation failures into fatal RegistryError exceptions
#TODO: Distinguish schema vs semantic validation failures in raised errors
#TODO: Ensure loader remains framework-agnostic (no FastAPI imports)


REGISTRY_DIR = Path("model_registry")


class RegistryError(Exception):
    """Raised when the model registry is invalid."""
    pass


@dataclass(frozen=True)
class ModelDefinition:
    model_id: str
    version: str
    raw: Dict[str, Any]


def load_model_registry() -> Dict[str, ModelDefinition]:
    """
    Load and validate all model registry files.

    Returns:
        Dict[str, ModelDefinition]: keyed by model_id

    Raises:
        RegistryError: if anything is invalid
    """
    if not REGISTRY_DIR.exists():
        raise RegistryError(f"Model registry directory not found: {REGISTRY_DIR}")

    if not REGISTRY_DIR.is_dir():
        raise RegistryError(f"Model registry path is not a directory: {REGISTRY_DIR}")

    model_files = sorted(REGISTRY_DIR.glob("*.json"))

    if not model_files:
        raise RegistryError("No model registry files found")

    registry: Dict[str, ModelDefinition] = {}

    for path in model_files:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise RegistryError(f"Invalid JSON in {path.name}: {e}") from e

        try:
            model_id = data["model_id"]
            version = data["version"]
        except KeyError as e:
            raise RegistryError(
                f"Missing required field {e.args[0]} in {path.name}"
            ) from e

        if model_id in registry:
            raise RegistryError(f"Duplicate model_id detected: {model_id}")

        registry[model_id] = ModelDefinition(
            model_id=model_id,
            version=version,
            raw=data,
        )

    return registry
