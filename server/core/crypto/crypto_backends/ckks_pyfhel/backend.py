from Pyfhel import Pyfhel, PyCtxt

from server.core.crypto.backend import CryptoBackend
from server.core.crypto.errors import (
    CiphertextDeserializationError,
    CiphertextIncompatibleError,
)


class PyfhelCKKSBackend(CryptoBackend):
    """
    Concrete CKKS backend using Pyfhel.

    Responsible for:
    - ciphertext deserialization
    - ciphertext/context compatibility checks
    - scale sanity checks
    """

    def deserialize_ciphertext(self, raw: bytes, context: Pyfhel) -> PyCtxt:
        try:
            return PyCtxt(pyfhel=context, bytestring=raw)
        except Exception as e:
            raise CiphertextDeserializationError(
                "Failed to deserialize CKKS ciphertext"
            ) from e

    def assert_ciphertext_compatible(self, ct: PyCtxt, context: Pyfhel) -> None:
        try:
            # Decryption will fail if ciphertext does not belong
            # to this context or uses incompatible parameters.
            context.decryptFrac(ct)
        except Exception as e:
            raise CiphertextIncompatibleError(
                "Ciphertext incompatible with server CKKS context"
            ) from e


    def assert_correct_scale(self, ct: PyCtxt, context: Pyfhel) -> None:
        """
        Ensure ciphertext scale is sane relative to context policy.
        """
        try:
            ct_scale = ct.scale
        except Exception as e:
            raise CiphertextIncompatibleError(
                "Unable to read ciphertext scale"
            ) from e

        expected_scale = context.scale

        if ct_scale <= 0 or ct_scale > expected_scale * 2:
            raise CiphertextIncompatibleError(
                f"Ciphertext scale {ct_scale} incompatible with expected scale {expected_scale}"
            )
