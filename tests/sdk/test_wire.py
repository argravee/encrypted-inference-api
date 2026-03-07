import pytest

from heapi_client.errors import CryptoError
from heapi_client.ckks.wire import (
    serialize_ciphertext,
    deserialize_ciphertext,
)


class FakeCiphertext:
    def __init__(self, data: bytes):
        self._data = data

    def to_bytes(self):
        return self._data


class FakeHE:
    def from_bytes_ciphertext(self, data: bytes):
        return {"ciphertext_bytes": data}


def test_serialize_ciphertext_returns_hex_payload():
    ct = FakeCiphertext(b"\xde\xad\xbe\xef")
    result = serialize_ciphertext(ct)

    assert result == {
        "encoding": "hex",
        "payload": "deadbeef",
    }


def test_deserialize_ciphertext_round_trips_hex():
    he = FakeHE()
    result = deserialize_ciphertext(he, "deadbeef")

    assert result == {"ciphertext_bytes": b"\xde\xad\xbe\xef"}


def test_deserialize_ciphertext_invalid_hex_raises_crypto_error():
    he = FakeHE()

    with pytest.raises(CryptoError, match="valid hex|deserialize"):
        deserialize_ciphertext(he, "not-hex")