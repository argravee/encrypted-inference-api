from heapi_client.errors import (
    APIError,
    CryptoError,
    JobFailedError,
    ProtocolError,
    SchemaValidationError,
    map_protocol_error,
)


def test_map_protocol_error_schema():
    err = map_protocol_error(
        {"error": {"code": "INVALID_SCHEMA", "message": "bad request"}}
    )
    assert isinstance(err, SchemaValidationError)


def test_map_protocol_error_crypto():
    err = map_protocol_error(
        {"error": {"code": "INVALID_CIPHERTEXT", "message": "scale mismatch"}}
    )
    assert isinstance(err, CryptoError)


def test_map_protocol_error_job_failed():
    err = map_protocol_error(
        {"error": {"code": "JOB_FAILED", "message": "worker crashed"}}
    )
    assert isinstance(err, JobFailedError)


def test_map_protocol_error_fallback():
    err = map_protocol_error(
        {"error": {"code": "SOMETHING_ELSE", "message": "oops"}}
    )
    assert isinstance(err, ProtocolError)


def test_api_error_contains_status_code_and_details():
    err = APIError(400, "bad request", details={"x": 1})
    assert err.status_code == 400
    assert err.details == {"x": 1}