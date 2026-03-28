from fastapi.testclient import TestClient
import numpy as np
from Pyfhel import PyCtxt

from server.app.main import app
from server.core.crypto.crypto_backends.ckks_pyfhel.context import generate_ckks_context
from server.core.model_registry.registry import MODEL_REGISTRY


def _build_crypto_params(model_raw: dict) -> dict:
    encryption_parameters = model_raw["encryption_parameters"]
    return {
        "scheme": model_raw["he_scheme"],
        "poly_modulus_degree": encryption_parameters["poly_modulus_degree"],
        "coeff_modulus_bits": encryption_parameters["coeff_modulus_bits"],
        "scale": encryption_parameters["scale"],
    }


def _encrypt_feature_vector(feature_vector: list[float], context) -> list[dict]:
    encrypted_inputs = []

    for value in feature_vector:
        pt = np.array([float(value)], dtype=np.float64)
        ct = context.encryptFrac(pt)
        encrypted_inputs.append(
            {
                "encoding": "hex",
                "payload": ct.to_bytes().hex(),
            }
        )

    return encrypted_inputs


def _decrypt_single_output(payload_hex: str, context) -> float:
    ct = PyCtxt(pyfhel=context, bytestring=bytes.fromhex(payload_hex))
    decrypted = context.decryptFrac(ct)

    if isinstance(decrypted, (list, tuple)):
        return float(decrypted[0])

    try:
        return float(decrypted)
    except TypeError:
        return float(decrypted[0])


def test_plain_and_encrypted_inference_agree():
    app.dependency_overrides.clear()
    client = TestClient(app)

    model_id = "logistic_v1"
    version = "1.0.0"

    model_meta = MODEL_REGISTRY[(model_id, version)]
    model_raw = model_meta.raw

    input_dimension = model_raw["inference"]["input_dimension"]
    feature_vector = [0.1] * input_dimension

    # 1. Plain inference
    plain_response = client.post(
        "/infer/plain",
        json={
            "model_id": model_id,
            "version": version,
            "inputs": feature_vector,
        },
    )
    assert plain_response.status_code == 200, plain_response.text
    plain_body = plain_response.json()
    plain_output = float(plain_body["outputs"][0])

    # 2. Build client-side CKKS context
    crypto_params = _build_crypto_params(model_raw)
    context = generate_ckks_context(crypto_params)
    context.keyGen()

    # 3. Encrypt each feature separately
    encrypted_inputs = _encrypt_feature_vector(feature_vector, context)

    # 4. Encrypted inference
    infer_response = client.post(
        "/infer",
        json={
            "model_id": model_id,
            "version": version,
            "batch_size": 1,
            "inputs": encrypted_inputs,
        },
    )
    assert infer_response.status_code == 200, infer_response.text
    infer_body = infer_response.json()
    job_id = infer_body["job_id"]

    # 5. Fetch completed result
    job_response = client.get(f"/jobs/{job_id}")
    assert job_response.status_code == 200, job_response.text
    job_body = job_response.json()
    result_payload = job_body["result"]["payload"]

    # 6. Decrypt encrypted output
    encrypted_output = _decrypt_single_output(result_payload, context)

    # 7. Compare outputs
    assert abs(plain_output - encrypted_output) < 1e-3

    app.dependency_overrides.clear()