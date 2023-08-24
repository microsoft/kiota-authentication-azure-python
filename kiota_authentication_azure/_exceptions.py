from builtins import Exception


class KiotaAuthenticationError(Exception):
    """Base class for all Kiota Authentication Azure errors."""


class HTTPError(KiotaAuthenticationError):
    """Error raised when the scheme fails https validation."""
