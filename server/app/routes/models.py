from fastapi import APIRouter
from core.model_registry.registry import MODEL_REGISTRY

router = APIRouter()

@router.get("/models")
def list_models():
    for item in MODEL_REGISTRY.values():

        data_projection = []
        model_id = item.model_id
        version= item.version
        he_scheme = item.raw["he_scheme"]
        input_dim = item.raw["inference"]["input_dimension"]
        output_dim = item.raw["inference"]["output_dimension"]
        max_batch_size = item.raw["constraints"]["max_batch_size"]

        data_projection.append({
            "model_id" : model_id,
            "version": version,
            "he_scheme": he_scheme,
            "input_dim": input_dim,
            "output_dim": output_dim,
            "max_batch_size" : max_batch_size
        })

    return data_projection





