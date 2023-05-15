import inspect
from typing import TYPE_CHECKING, Dict, List, Optional, Union
from urllib.parse import urlparse

from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from kiota_abstractions.authentication import AccessTokenProvider, AllowedHostsValidator


class AzureIdentityAccessTokenProvider(AccessTokenProvider):
    """Access token provider that leverages the Azure Identity library to retrieve an access token.
    """

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

    async def get_authorization_token(self, uri: str) -> str:
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

        if not self._scopes:
            self._scopes = [f"{parsed_url.scheme}://{parsed_url.netloc}/.default"]
        #async credentials
        if inspect.iscoroutinefunction(self._credentials.get_token):
            if self._options:
                result = await self._credentials.get_token(*self._scopes, **self._options)
            else:
                result = await self._credentials.get_token(*self._scopes)
            await self._credentials.close()  #type: ignore
        # sync credentials
        else:
            if self._options:
                result = self._credentials.get_token(*self._scopes, **self._options)
            else:
                result = self._credentials.get_token(*self._scopes)

        if result and result.token:
            return result.token
        return ""

    def get_allowed_hosts_validator(self) -> AllowedHostsValidator:
        """Retrieves the allowed hosts validator.
        Returns:
            AllowedHostsValidator: The allowed hosts validator.
        """
        return self._allowed_hosts_validator
