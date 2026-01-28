from crypto_backends.ckks_pyfhel.backend import PyfhelCKKSBackend
from crypto_backends.ckks_pyfhel.context import CKKS_CONTEXT


def get_crypto_backend():
    """
    Returns the concrete crypto backend implementation.
    """
    return PyfhelCKKSBackend()


def get_crypto_context():
    """
    Returns the server-wide CKKS context.
    """
    return CKKS_CONTEXT
