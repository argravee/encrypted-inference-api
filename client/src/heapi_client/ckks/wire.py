from __future__ import annotations
from Pyfhel import PyCtxt
from heapi_client.errors import CryptoError
from ..errors import CryptoError

BINARY_ENCODING = "hex"


def serialize_ciphertext(ciphertext) -> dict:
    """
    Convert a Pyfhel ciphertext into the protocol request shape:
    {
      "encoding": "hex",
      "payload": "..."
    }
    """
    try:
        ct_bytes = ciphertext.to_bytes()
    except Exception as exc:
        raise CryptoError(f"Failed to serialize ciphertext: {exc}") from exc

    return {
        "encoding": BINARY_ENCODING,
        "payload": ct_bytes.hex(),
    }


def deserialize_ciphertext(he, payload: str):
    """
    Convert the protocol response payload string back into a Pyfhel ciphertext.
    The protocol uses hex-encoded ciphertext bytes.
    """
    if not isinstance(payload, str):
        raise CryptoError("Ciphertext payload must be a string")

    try:
        ct_bytes = bytes.fromhex(payload)
    except ValueError as exc:
        raise CryptoError("Ciphertext payload is not valid hex") from exc

    try:
        return PyCtxt(pyfhel=he, bytestring=ct_bytes)
    except Exception as exc:
        raise CryptoError(f"Failed to deserialize ciphertext: {exc}") from exc