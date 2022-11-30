from dataclasses import dataclass


@dataclass
class DummyToken:
    token: str


class DummySyncAzureTokenCredential():

    def get_token(self, *args):
        return DummyToken(token="This is a dummy token")

class DummyAsyncAzureTokenCredential():

    async def get_token(self, *args):
        return DummyToken(token="This is a dummy token")

    async def close(self, *args):
        pass
