from pathlib import Path
import json
from dataclasses import dataclass
from typing import Dict, Any, List
from core.model_registry.schema_validation import validate_model_registry_entry
from core.model_registry.semantic_validation import semantic_model_registry_validation

REGISTRY_DIR = Path(__file__).resolve().parent

#TODO: move into its own errors file
class RegistryError(Exception):
    """Raised when the model registry is invalid."""
    pass

"""
Creates a dataclass to hold the extracted strings from the model
"""
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

    model_files = [
        p for p in REGISTRY_DIR.glob("*.json")
        if p.name != "model_registry_entry.schema.json"
    ]



    if not model_files:
        raise RegistryError("No model registry files found")

    registry: dict[tuple[str, str], ModelDefinition]= {}

    for path in model_files:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise RegistryError(f"Invalid JSON in {path.name}: {e}") from e

        try:
            validate_model_registry_entry(data)
        except Exception as e:
            raise RegistryError(
                f"Schema validation failed for {path.name}: {e}"
            ) from e

        try:
            semantic_model_registry_validation(data)
        except Exception as e:
            raise RegistryError(
                f"Semantic validation failed for {path.name}: {e}"
            ) from e


        try:
            model_id = data["model_id"]
            version = data["version"]
        except KeyError as e:
            raise RegistryError(
                f"Missing required field {e.args[0]} in {path.name}"
            ) from e

        if model_id in registry:
            raise RegistryError(f"Duplicate model_id detected: {model_id}")

        identity = (model_id, version)

        if identity in registry:
            raise RegistryError(
                f"Duplicate model identity detected: model_id={model_id}, version={version}"
            )


        registry[identity] = ModelDefinition(
            model_id=model_id,
            version=version,
            raw=data,
        )

        if not registry:
            raise RegistryError(f"Registry is empty")

    if not any(
            model.raw["he_scheme"]=="CKKS"
            for model in registry.values()
    ):
        raise RegistryError("Model registry contains no CKKS compatible models")
    return registry
