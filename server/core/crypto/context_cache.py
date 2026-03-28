from __future__ import annotations

from functools import lru_cache

from server.core.crypto.crypto_backends.ckks_pyfhel.context import generate_ckks_context


@lru_cache(maxsize=16)
def get_cached_ckks_context(
        scheme: str,
        poly_modulus_degree: int,
        coeff_modulus_bits: tuple[int, ...],
        scale: float,
):
    crypto_params = {
        "scheme": scheme,
        "poly_modulus_degree": poly_modulus_degree,
        "coeff_modulus_bits": list(coeff_modulus_bits),
        "scale": scale,
    }
    return generate_ckks_context(crypto_params)


def clear_ckks_context_cache() -> None:
    get_cached_ckks_context.cache_clear()