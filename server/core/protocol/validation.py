from core.protocol.errors import (
    MissingApiVersionError,
    UnknownRequestTypeError,
    MissingPayloadError, InvalidEnvelopeError, UnsupportedApiVersionError, MissingRequestTypeError,
)

def validate_envelope(envelope: dict) -> None:
    if not isinstance(envelope, dict):
        raise InvalidEnvelopeError()

    if "api_version" not in envelope:
        raise MissingApiVersionError()

    if envelope["api_version"] != "v1":
        raise UnsupportedApiVersionError(envelope["api_version"])

    if "type" not in envelope:
        raise MissingRequestTypeError()

    if envelope["type"] not in {"infer"}:
        raise UnknownRequestTypeError(envelope["type"])

    if "payload" not in envelope:
        raise MissingPayloadError()
