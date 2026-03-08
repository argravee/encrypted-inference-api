from __future__ import annotations

from Pyfhel import PyCtxt, Pyfhel

from server.core.crypto.backend import CryptoBackend
from server.core.crypto.errors import (
    CiphertextDeserializationError,
    CiphertextIncompatibleError,
)


class PyfhelCKKSBackend(CryptoBackend):
    def deserialize_ciphertext(self, raw: bytes, context: Pyfhel) -> PyCtxt:
        try:
            return PyCtxt(pyfhel=context, bytestring=raw)
        except Exception as e:
            raise CiphertextDeserializationError(
                "Failed to deserialize CKKS ciphertext"
            ) from e

    def assert_ciphertext_compatible(self, ct: PyCtxt, context: Pyfhel) -> None:
        if ct is None:
            raise CiphertextIncompatibleError("Ciphertext is None")

    def assert_correct_scale(self, ct: PyCtxt, context: Pyfhel) -> None:
        try:
            ct_scale = ct.scale
        except Exception as e:
            raise CiphertextIncompatibleError(
                "Unable to read ciphertext scale"
            ) from e

        expected_scale = context.scale
        if ct_scale <= 0 or ct_scale > expected_scale * 4:
            raise CiphertextIncompatibleError(
                f"Ciphertext scale {ct_scale} incompatible with expected scale {expected_scale}"
            )