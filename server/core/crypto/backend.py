# core/crypto/backend.py
from typing import Protocol, Any

class CryptoBackend(Protocol):
    def deserialize_ciphertext(self, raw: bytes, context: Any) -> Any:
        """
        Deserialize raw ciphertext bytes into a backend-specific ciphertext.

        Must raise on failure.
        """
        ...

    def assert_ciphertext_compatible(self,ct: Any, context: Any)->None:
        ...
    def assert_correct_scale(self,ct: Any, context: Any)->None:
        ...