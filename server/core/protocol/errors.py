class EnvelopeError(Exception):
    """Base class for all envelope-level protocol errors."""
    pass


class InvalidEnvelopeError(EnvelopeError):
    pass


class MissingApiVersionError(EnvelopeError):
    pass


class UnsupportedApiVersionError(EnvelopeError):
    pass


class MissingRequestTypeError(EnvelopeError):
    pass


class UnknownRequestTypeError(EnvelopeError):
    pass


class MissingPayloadError(EnvelopeError):
    pass


class InvalidPayloadContainerError(EnvelopeError):
    pass
