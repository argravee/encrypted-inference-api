from fastapi import APIRouter

from server.core.model_registry.registry import MODEL_REGISTRY

router = APIRouter()


@router.get("/models")
def list_models():
    models = [
        definition.raw
        for _, definition in sorted(MODEL_REGISTRY.items(), key=lambda item: item[0])
    ]

    return {
        "api_version": "1.0.0",
        "models": models,
    }