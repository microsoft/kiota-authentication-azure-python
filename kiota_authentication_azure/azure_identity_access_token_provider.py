import inspect
from pickle import TRUE
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

from azure.core.credentials import AccessToken, TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from kiota_abstractions.authentication import AccessTokenProvider, AllowedHostsValidator

from ._exceptions import HTTPError
from ._observability import Observability


class AzureIdentityAccessTokenProvider(AccessTokenProvider):
    """Access token provider that leverages the Azure Identity library to retrieve an access token.
    """

    IS_VALID_URL = "com.microsoft.kiota.authentication.is_url_valid"
    SCOPES = "com.microsoft.kiota.authentication.scopes"
    ADDITIONAL_CLAIMS_PROVIDED = "com.microsoft.kiota.authentication.additional_claims_provided"

    def __init__(
        self,
        credentials: Union['TokenCredential', 'AsyncTokenCredential'],
        options: Optional[Dict],
        scopes: List[str] = [],
        allowed_hosts: List[str] = [],
    ) -> None:
        if not credentials:
            raise ValueError("Parameter credentials cannot be null")
        list_error = "should be an empty list or a list of strings"
        if not isinstance(scopes, list):
            raise TypeError(f"Scopes {list_error}")
        if not isinstance(allowed_hosts, list):
            raise TypeError(f"Allowed hosts {list_error}")

        self._credentials = credentials
        self._scopes = scopes
        self._options = options
        self._allowed_hosts_validator = AllowedHostsValidator(allowed_hosts)
        self._observability = Observability()

    async def get_authorization_token(self, uri: str) -> str:
        """This method is called by the BaseBearerTokenAuthenticationProvider class to get the
        access token.
        Args:
            uri (str): The target URI to get an access token for.
        Returns:
            str: The access token to use for the request.
        """
        span = self._observability.start_tracing_span(uri, "get_authorization_token")
        try:
            if not self.get_allowed_hosts_validator().is_url_host_valid(uri):
                span.set_attribute(self.IS_VALID_URL, False)
                return ""

            parsed_url = urlparse(uri)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                span.set_attribute(self.IS_VALID_URL, False)
                exc = HTTPError("Only https scheme with a valid host are supported")
                span.record_exception(exc)
                raise exc

            if not parsed_url.scheme == 'https':
                span.set_attribute(self.IS_VALID_URL, False)
                exc = HTTPError("Only https is supported")
                span.record_exception(exc)
                raise exc

            span.set_attribute(self.IS_VALID_URL, TRUE)
            if not self._scopes:
                self._scopes = [f"{parsed_url.scheme}://{parsed_url.netloc}/.default"]
            span.set_attribute(self.SCOPES, ",".join(self._scopes))
            span.set_attribute(self.ADDITIONAL_CLAIMS_PROVIDED, bool(self._options))

            if self._options:
                result = self._credentials.get_token(*self._scopes, **self._options)
            else:
                result = self._credentials.get_token(*self._scopes)

            if inspect.isawaitable(result):
                result = await result

            if result and isinstance(result, AccessToken):
                return result.token
            return ""
        finally:
            span.end()

    def get_allowed_hosts_validator(self) -> AllowedHostsValidator:
        """Retrieves the allowed hosts validator.
        Returns:
            AllowedHostsValidator: The allowed hosts validator.
        """
        return self._allowed_hosts_validator
