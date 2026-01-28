import numpy as np

from server.core.crypto.crypto_backends.ckks_pyfhel.context import CKKS_CONTEXT
from server.core.crypto.crypto_backends.ckks_pyfhel.backend import PyfhelCKKSBackend


def test_ckks_roundtrip():
    backend = PyfhelCKKSBackend()
    HE = CKKS_CONTEXT

    # --- Key generation (client-side simulation) ---
    HE.keyGen()

    # --- Encrypt a value (CKKS requires numpy array) ---
    value = np.array([3.14159], dtype=float)
    ct = HE.encryptFrac(value)

    # --- Serialize ciphertext (what client sends) ---
    raw = ct.to_bytes()

    # --- Server-side: deserialize ---
    ct2 = backend.deserialize_ciphertext(raw, HE)

    # --- Server-side: validate ---
    backend.assert_ciphertext_compatible(ct2, HE)
    backend.assert_correct_scale(ct2, HE)

    # --- Decrypt result ---
    decrypted = HE.decryptFrac(ct2)

    assert abs(decrypted[0] - value[0]) < 1e-3
