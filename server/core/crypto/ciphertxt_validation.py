from server.core.crypto.backend import CryptoBackend
from server.core.crypto.errors import (
    CiphertextDeserializationError,
    CiphertextIncompatibleError,
)
from server.core.model_registry.loader import ModelDefinition


def validate_ciphertext_structure(
        raw_ciphertext: bytes,
        model_meta: ModelDefinition,
        context,
        backend: CryptoBackend,
):
    """
    Layer 2 validation:
    - Safely deserialize ciphertext
    - Verify scheme compatibility
    - Verify polynomial modulus degree
    - Sanity-check scale
    """

    try:
        ct = backend.deserialize_ciphertext(raw_ciphertext, context)
    except CiphertextDeserializationError:
        raise

    if ct is None:
        raise CiphertextDeserializationError("cipher deserialized to None")

    if model_meta.raw["he_scheme"] != "CKKS":
        raise CiphertextIncompatibleError("Model expects CKKS")

    backend.assert_ciphertext_compatible(ct, context)
    backend.assert_correct_scale(ct, context)

    return ct