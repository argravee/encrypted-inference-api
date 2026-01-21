from fastapi import APIRouter, HTTPException
from fastapi import Depends

from core.crypto.backend import CryptoBackend
from core.crypto.ciphertxt_validation import validate_ciphertext_structure
from core.crypto.dependencies import (
    get_crypto_backend,
    get_crypto_context,
)
from core.jobs.queue import enqueue_job, dequeue_worker
from core.model_registry.registry import MODEL_REGISTRY
from core.protocol.envelope_validation import validate_envelope

router = APIRouter()

@router.post("/infer")
def infer(
        envelope: dict,
        backend: CryptoBackend = Depends(get_crypto_backend),
        context = Depends(get_crypto_context),

):
    validate_envelope(envelope)
    model_id = envelope["model_id"]
    raw_ciphertxt = envelope["ciphertext"]

    model_meta = MODEL_REGISTRY.get(model_id)
    if model_meta is None:
        raise HTTPException(status_code=404, detail="Unknown model")

    validate_ciphertext_structure(
        raw_ciphertext=raw_ciphertxt,
        model_meta=model_meta,
        context=context,
        backend=backend,
    )
    job_id = enqueue_job(model_id=model_id, ciphertext_b64=envelope["ciphertext"])
    return {"status": "accepted", "job_id": job_id}



