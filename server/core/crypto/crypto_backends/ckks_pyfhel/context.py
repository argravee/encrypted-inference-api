from Pyfhel import Pyfhel
from dataclasses import dataclass

"""
sets params for CKKS encryption
generates module level context
"""

@dataclass(frozen=True)
class CKKSParams:
    scheme: str = "CKKS"
    polynomial_modulus_degree: int = 16384
    coeff_modulus_bits: tuple[int,...] = (60, 30, 30, 60)
    scale: int = 2**30

def generate_ckks_context(params: CKKSParams)-> Pyfhel:

    he = Pyfhel()
    he.contextGen(
        scheme=params.scheme,
        n=params.polynomial_modulus_degree,
        scale=params.scale,
        qi_sizes=list(params.coeff_modulus_bits),
    )
    return he

CKKS_CONTEXT = generate_ckks_context(CKKSParams())
