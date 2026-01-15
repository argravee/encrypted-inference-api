from fastapi import HTTPException
from core.crypto.backend import CryptoBackend

def get_crypto_backend()->CryptoBackend:
    raise HTTPException(status_code=503,detail="Cryptobackend.py not configured")


def get_crypto_context():
    raise HTTPException(
        status_code=503,
        detail="Crypto context not configured"
        # Backend-specific cryptographic
        # context (to be provided by implementation)
    )