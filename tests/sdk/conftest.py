import json
import pytest


def write_json(tmp_path, name, payload):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


@pytest.fixture
def get_models_response():
    return {
        "api_version": "1.0.0",
        "models": [
            {
                "model_id": "logistic_v1",
                "version": "1.0.0",
                "description": "Encrypted logistic regression for binary classification",
                "he_scheme": "CKKS",
                "encryption_parameters": {
                    "poly_modulus_degree": 16384,
                    "scale": 1073741824,
                    "coeff_modulus_bits": [60, 30, 30, 60],
                    "max_multiplicative_depth": 2,
                },
                "inference": {
                    "input_dimension": 8,
                    "output_dimension": 1,
                    "activation": "polynomial_sigmoid_v1",
                },
                "constraints": {
                    "max_batch_size": 16,
                },
            }
        ],
    }


@pytest.fixture
def get_models_schema():
    return {
        "type": "object",
        "properties": {
            "api_version": {"type": "string"},
            "models": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "model_id": {"type": "string"},
                        "version": {"type": "string"},
                        "description": {"type": "string"},
                        "he_scheme": {"type": "string"},
                        "encryption_parameters": {
                            "type": "object",
                            "properties": {
                                "poly_modulus_degree": {"type": "integer"},
                                "scale": {"type": "number"},
                                "coeff_modulus_bits": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                },
                                "max_multiplicative_depth": {"type": "integer"},
                            },
                            "required": [
                                "poly_modulus_degree",
                                "scale",
                                "coeff_modulus_bits",
                            ],
                        },
                        "inference": {
                            "type": "object",
                            "properties": {
                                "input_dimension": {"type": "integer"},
                                "output_dimension": {"type": "integer"},
                                "activation": {"type": "string"},
                            },
                            "required": ["input_dimension", "output_dimension"],
                        },
                        "constraints": {
                            "type": "object",
                            "properties": {
                                "max_batch_size": {"type": "integer"},
                            },
                        },
                    },
                    "required": [
                        "model_id",
                        "version",
                        "he_scheme",
                        "encryption_parameters",
                        "inference",
                    ],
                },
            },
        },
        "required": ["api_version", "models"],
    }


@pytest.fixture
def infer_request_schema():
    return {
        "type": "object",
        "properties": {
            "model_id": {"type": "string"},
            "version": {"type": "string"},
            "inputs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "encoding": {"type": "string"},
                        "payload": {"type": "string"},
                    },
                    "required": ["encoding", "payload"],
                },
            },
        },
        "required": ["model_id", "version", "inputs"],
    }


@pytest.fixture
def infer_response_schema():
    return {
        "type": "object",
        "properties": {
            "model_id": {"type": "string"},
            "version": {"type": "string"},
            "payload": {"type": "string"},
            "diagnostics": {
                "type": "object",
                "properties": {
                    "requested_batch_size": {"type": "integer", "minimum": 1},
                    "processed_batch_size": {"type": "integer", "minimum": 1},
                    "batch_truncated": {"type": "boolean"},
                },
                "required": [
                    "requested_batch_size",
                    "processed_batch_size",
                    "batch_truncated",
                ],
            },
        },
        "required": ["model_id", "version", "payload"],
    }


@pytest.fixture
def model_metadata(get_models_response):
    return get_models_response["models"][0]


@pytest.fixture
def infer_response_payload():
    return {
        "model_id": "logistic_v1",
        "version": "1.0.0",
        "payload": "deadbeef",
        "diagnostics": {
            "requested_batch_size": 1,
            "processed_batch_size": 1,
            "batch_truncated": False,
        },
    }