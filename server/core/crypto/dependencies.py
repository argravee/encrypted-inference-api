from server.core.crypto.backend import CryptoBackend
from server.core.crypto.crypto_backends.ckks_pyfhel.backend import PyfhelCKKSBackend


def get_crypto_backend() -> CryptoBackend:
    return PyfhelCKKSBackend()