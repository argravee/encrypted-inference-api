import numpy as np

from server.core.crypto.crypto_backends.ckks_pyfhel.backend import PyfhelCKKSBackend
from server.core.crypto.crypto_backends.ckks_pyfhel.context import CKKS_CONTEXT


def test_ckks_roundtrip():
    backend = PyfhelCKKSBackend()
    he = CKKS_CONTEXT

    he.keyGen()

    value = np.array([3.14159], dtype=float)
    ct = he.encryptFrac(value)

    raw = ct.to_bytes()

    ct2 = backend.deserialize_ciphertext(raw, he)
    backend.assert_ciphertext_compatible(ct2, he)
    backend.assert_correct_scale(ct2, he)

    decrypted = he.decryptFrac(ct2)

    assert abs(decrypted[0] - value[0]) < 1e-3