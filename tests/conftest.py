from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_model_dict() -> dict:
    return {
        "model_id": "logistic_v1",
        "version": "1.0.0",
        "description": "Reference logistic model",
        "he_scheme": "CKKS",
        "encryption_parameters": {
            "poly_modulus_degree": 16384,
            "scale": 1073741824.0,
            "coeff_modulus_bits": [60, 30, 30, 60],
            "max_multiplicative_depth": 2,
        },
        "inference": {
            "input_dimension": 8,
            "output_dimension": 1,
            "activation": "polynomial_sigmoid_v1",
        },
        "parameters": {
            "weights": [0.001] * 8,
            "bias": 0.0,
        },
        "activation_parameters": {
            "kind": "polynomial_sigmoid_v1",
            "coefficients": [0.5, 0.15, -0.01],
        },
        "constraints": {
            "max_batch_size": 16,
        },
    }


@pytest.fixture
def sample_model_definition(sample_model_dict):
    return SimpleNamespace(
        model_id=sample_model_dict["model_id"],
        version=sample_model_dict["version"],
        raw=sample_model_dict,
    )