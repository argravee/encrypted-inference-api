from core.model_registry.loader import ModelDefinition
from core.crypto.backend import CryptoBackend
from core.crypto.errors import (
    CiphertextDeserializationError,
    CiphertextIncompatibleError,
)

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
    - Reject malformed or dangerous ciphertexts
    """

    # 1. Attempt deserialization (TODO:400 if fails)
    try:
        ct = backend.deserialize_ciphertext(raw_ciphertext,context)
    except CiphertextDeserializationError:
        raise

    # 2. Verify scheme matches expected HE scheme
    if model_meta.raw["he_scheme"] != "CKKS":
        raise CiphertextIncompatibleError("Model expects CKKS")

    # 3. Verify polynomial modulus degree
    backend.assert_ciphertext_compatible(ct,context)

    # 4. Sanity-check scale (CKKS only)
    backend.assert_correct_scale(ct,context)

    # 5. Ensure ciphertext has data
    if ct is None:
        raise CiphertextDeserializationError("cipher deserialized to None")

    return ct