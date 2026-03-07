import pytest


pytestmark = pytest.mark.integration


def _normalize_result(result):
    """
    Normalize decrypted SDK output into a plain Python list of numbers.
    """
    if hasattr(result, "tolist"):
        result = result.tolist()

    if isinstance(result, (int, float)):
        return [float(result)]

    if isinstance(result, tuple):
        return list(result)

    if isinstance(result, list):
        return result

    raise AssertionError(f"Unexpected decrypted result type: {type(result)!r}")


def test_live_model_discovery_returns_usable_metadata(live_models, live_model):
    assert isinstance(live_models, list)
    assert len(live_models) >= 1

    assert isinstance(live_model.get("model_id"), str)
    assert isinstance(live_model.get("version"), str)

    assert live_model.get("he_scheme") == "CKKS"

    params = live_model.get("encryption_parameters", {})
    assert isinstance(params.get("poly_modulus_degree"), int)
    assert isinstance(params.get("scale"), (int, float))
    assert isinstance(params.get("coeff_modulus_bits"), list)

    inference = live_model.get("inference", {})
    assert isinstance(inference.get("input_dimension"), int)
    assert isinstance(inference.get("output_dimension"), int)


def test_live_sdk_single_inference_roundtrip(
        live_client,
        live_model,
        live_version,
        live_single_input,
):
    result = live_client.infer(
        model_id=live_model["model_id"],
        version=live_version,
        values=live_single_input,
    )

    normalized = _normalize_result(result)

    assert all(isinstance(x, (int, float)) for x in normalized)

    expected_output_dimension = live_model.get("inference", {}).get("output_dimension")
    if isinstance(expected_output_dimension, int) and expected_output_dimension >= 1:
        assert len(normalized) == expected_output_dimension