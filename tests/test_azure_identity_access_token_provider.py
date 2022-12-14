import pytest
from kiota_abstractions.authentication import AllowedHostsValidator

from kiota_authentication_azure.azure_identity_access_token_provider import (
    AzureIdentityAccessTokenProvider,
)

from .helpers import DummyAsyncAzureTokenCredential, DummySyncAzureTokenCredential


def test_invalid_instantiation_without_credentials():
    with pytest.raises(Exception):
        token_provider = AzureIdentityAccessTokenProvider(None, None)


def test_valid_instantiation_without_options():
    token_provider = AzureIdentityAccessTokenProvider(DummyAsyncAzureTokenCredential(), None)
    assert not token_provider._options


def test_invalid_instatiation_without_scopes():
    with pytest.raises(Exception):
        token_provider = AzureIdentityAccessTokenProvider(
            DummyAsyncAzureTokenCredential(), None, None
        )


def test_get_allowed_hosts_validator():
    token_provider = AzureIdentityAccessTokenProvider(DummySyncAzureTokenCredential(), None)
    validator = token_provider.get_allowed_hosts_validator()
    hosts = validator.get_allowed_hosts()
    assert isinstance(validator, AllowedHostsValidator)
    assert 'graph.microsoft.com' in hosts
    assert 'graph.microsoft.us' in hosts
    assert 'graph.microsoft.de' in hosts
    assert 'microsoftgraph.chinacloudapi.cn' in hosts
    assert 'canary.graph.microsoft.com' in hosts


@pytest.mark.asyncio
async def test_get_authorization_token_async():

    token_provider = AzureIdentityAccessTokenProvider(DummyAsyncAzureTokenCredential(), None)
    token = await token_provider.get_authorization_token('https://graph.microsoft.com')
    assert token == "This is a dummy token"


@pytest.mark.asyncio
async def test_get_authorization_token_sync():

    token_provider = AzureIdentityAccessTokenProvider(DummySyncAzureTokenCredential(), None)
    token = await token_provider.get_authorization_token('https://graph.microsoft.com')
    assert token == "This is a dummy token"


@pytest.mark.asyncio
async def test_get_authorization_token_invalid_url():

    token_provider = AzureIdentityAccessTokenProvider(DummyAsyncAzureTokenCredential(), None)
    token = await token_provider.get_authorization_token('https://example.com')
    assert token == ""


@pytest.mark.asyncio
async def test_get_authorization_token_invalid_scheme():
    with pytest.raises(Exception):
        token_provider = AzureIdentityAccessTokenProvider(DummySyncAzureTokenCredential(), None)
        token = await token_provider.get_authorization_token('http://graph.microsoft.com')
