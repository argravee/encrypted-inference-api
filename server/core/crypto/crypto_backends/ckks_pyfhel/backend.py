# core/crypto/backends/backend.py
from Pyfhel import Pyfhel, PyCtxt
from core.crypto.errors import CiphertextDeserializationError

class PyfhelCKKSBackend:
    def deserialize_ciphertext(self, raw: bytes, context: Pyfhel) -> PyCtxt:
        try:
            return PyCtxt(pyfhel=context, bytestring=raw)
        except Exception as e:
            raise CiphertextDeserializationError(
                "Failed to deserialize CKKS ciphertext"
            ) from e
