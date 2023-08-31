import base64
import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from kiota_abstractions.authentication import AccessTokenProvider, AllowedHostsValidator


class AzureIdentityAccessTokenProvider(AccessTokenProvider):
    """Access token provider that leverages the Azure Identity library to retrieve an access token.
    """
    CLAIMS_KEY = "claims"

    def __init__(
        self,
        credentials: Union[TokenCredential, AsyncTokenCredential],
        options: Optional[Dict],
        scopes: List[str] = [],
        allowed_hosts: List[str] = [],
    ) -> None:
        if not credentials:
            raise Exception("Parameter credentials cannot be null")
        list_error = "should be an empty list or a list of strings"
        if not isinstance(scopes, list):
            raise TypeError(f"Scopes {list_error}")
        if not isinstance(allowed_hosts, list):
            raise TypeError(f"Allowed hosts {list_error}")

        self._credentials = credentials
        self._scopes = scopes
        self._options = options
        self._allowed_hosts_validator = AllowedHostsValidator(allowed_hosts)

    async def get_authorization_token(
        self, uri: str, additional_authentication_context: Dict[str, Any] = {}
    ) -> str:
        """This method is called by the BaseBearerTokenAuthenticationProvider class to get the
        access token.
        Args:
            uri (str): The target URI to get an access token for.
        Returns:
            str: The access token to use for the request.
        """
        if not self.get_allowed_hosts_validator().is_url_host_valid(uri):
            return ""

        parsed_url = urlparse(uri)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise Exception("Only https scheme with a valid host are supported")

        if not parsed_url.scheme == 'https':
            raise Exception("Only https is supported")

        decoded_claim = None
        if all(
            [
                additional_authentication_context, self.CLAIMS_KEY
                in additional_authentication_context,
                isinstance(additional_authentication_context.get(self.CLAIMS_KEY), str)
            ]
        ):
            decoded_bytes = base64.b64decode(additional_authentication_context[self.CLAIMS_KEY])
            decoded_claim = decoded_bytes.decode("utf-8")

        if not self._scopes:
            self._scopes = [f"{parsed_url.scheme}://{parsed_url.netloc}/.default"]

        if self._options:
            result = self._credentials.get_token(
                *self._scopes, claims=decoded_claim, **self._options
            )
        else:
            result = self._credentials.get_token(*self._scopes, claims=decoded_claim)

        if inspect.isawaitable(result):
            result = await result
            await self._credentials.close()  #type: ignore

        if result and result.token:  #type: ignore
            return result.token  #type: ignore
        return ""

    def get_allowed_hosts_validator(self) -> AllowedHostsValidator:
        """Retrieves the allowed hosts validator.
        Returns:
            AllowedHostsValidator: The allowed hosts validator.
        """
        return self._allowed_hosts_validator
