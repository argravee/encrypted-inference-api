from __future__ import annotations


def _apply_polynomial_sigmoid(linear_ct, coefficients, context):
    if not coefficients:
        raise ValueError("Polynomial sigmoid coefficients are required")

    result = None

    for degree, coeff in enumerate(coefficients):
        if coeff == 0:
            continue

        if degree == 0:
            term = coeff
        elif degree == 1:
            term = linear_ct * coeff
        else:
            term = linear_ct ** degree
            if coeff != 1:
                term = term * coeff

        if result is None:
            result = term
        else:
            result = result + term

    if result is None:
        raise ValueError("Polynomial sigmoid cannot be identically zero")

    return result


def evaluate_encrypted_logistic(feature_ciphertexts, model_raw, context):
    parameters = model_raw["parameters"]
    weights = parameters["weights"]
    bias = parameters["bias"]

    if len(feature_ciphertexts) != len(weights):
        raise ValueError(
            f"Expected {len(weights)} feature ciphertexts, got {len(feature_ciphertexts)}"
        )

    linear_ct = None

    for ct, weight in zip(feature_ciphertexts, weights):
        weighted = ct * weight
        if linear_ct is None:
            linear_ct = weighted
        else:
            linear_ct = linear_ct + weighted

    if linear_ct is None:
        raise ValueError("No feature ciphertexts provided")

    linear_ct = linear_ct + bias

    activation_parameters = model_raw["activation_parameters"]
    coefficients = activation_parameters["coefficients"]

    return _apply_polynomial_sigmoid(linear_ct, coefficients, context)