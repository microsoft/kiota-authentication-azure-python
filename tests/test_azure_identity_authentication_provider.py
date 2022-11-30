import pytest
from kiota_abstractions.request_information import RequestInformation
from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider,
)
from .helpers import DummyAsyncAzureTokenCredential, DummySyncAzureTokenCredential

def test_invalid_instantiation_without_credentials():
    with pytest.raises(Exception):
        auth_provider = AzureIdentityAuthenticationProvider(None)


@pytest.mark.asyncio
async def test_valid_instantiation_without_options():
    auth_provider = AzureIdentityAuthenticationProvider(DummyAsyncAzureTokenCredential())
    request_info = RequestInformation()
    request_info.url = "https://graph.microsoft.com"
    await auth_provider.authenticate_request(request_info)
    assert isinstance(auth_provider, AzureIdentityAuthenticationProvider)
    assert 'authorization' in request_info.request_headers
