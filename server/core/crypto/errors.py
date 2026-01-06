# core/crypto/errors.py
class CiphertextDeserializationError(Exception):
    """Ciphertext could not be deserialized (malformed)."""

class CiphertextIncompatibleError(Exception):
    """Ciphertext is valid but incompatible with the model."""
