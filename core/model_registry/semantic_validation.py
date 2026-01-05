from typing import Any

def semantic_model_registry_validation(entry: dict[str,Any])->None:
    he_scheme = entry["he_scheme"]

    encryption_parameters = entry["encryption_parameters"]
    poly_modulus_degree = encryption_parameters["poly_modulus_degree"]
    scale = encryption_parameters["scale"]
    coeff_modulus_bits = encryption_parameters["coeff_modulus_bits"]
    max_multiplicative_depth = encryption_parameters["max_multiplicative_depth"]

    inference = entry["inference"]
    input_dimension = inference ["input_dimension"]
    output_dimension = inference ["output_dimension"]
    activation = inference ["activation"]

    constraints = entry["constraints"]
    max_batch_size = constraints["max_batch_size"]

    if he_scheme != "CKKS":
        raise ValueError(f"Invalid he_scheme. expected:CKKS got:{he_scheme}")

    if poly_modulus_degree <= 0 or (poly_modulus_degree & (poly_modulus_degree - 1)) != 0:
        raise ValueError(
            f"poly_modulus_degree must be a positive power of two, got {poly_modulus_degree}"
        )

    if max_multiplicative_depth < 0:
        raise ValueError(
            f"max_multiplicative_depth must be non-negative, got {max_multiplicative_depth}"
        )

    if max_multiplicative_depth > len(coeff_modulus_bits) - 1:
        raise ValueError(
            "max_multiplicative_depth exceeds available coeff_modulus_bits levels"
        )

    #Enforce activation–depth compatibility
    if activation == "polynomial_sigmoid_v1" and max_multiplicative_depth < 2:
        raise ValueError(
            "polynomial_sigmoid_v1 requires max_multiplicative_depth >= 2"
        )

    #Reject invalid dimension relationships
    if input_dimension <= 0:
        raise ValueError(
            f"input_dimension must be positive, got {input_dimension}"
        )

    if output_dimension <= 0:
        raise ValueError(
            f"output_dimension must be positive, got {output_dimension}"
        )

    # Logistic regression semantic invariant
    if output_dimension != 1:
        raise ValueError(
            f"logistic regression requires output_dimension == 1, got {output_dimension}"
        )

    #Reject invalid constraint relationships
    if max_batch_size <= 0:
        raise ValueError(
            f"max_batch_size must be positive, got {max_batch_size}"
        )

    if max_batch_size > poly_modulus_degree:
        raise ValueError(
            "max_batch_size cannot exceed poly_modulus_degree (packing limit)"
        )

    return None


