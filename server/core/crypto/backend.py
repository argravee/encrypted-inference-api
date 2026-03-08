from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CryptoBackend(ABC):
    @abstractmethod
    def deserialize_ciphertext(self, raw: bytes, context: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def assert_ciphertext_compatible(self, ct: Any, context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def assert_correct_scale(self, ct: Any, context: Any) -> None:
        raise NotImplementedError