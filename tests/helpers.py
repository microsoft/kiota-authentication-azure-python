from dataclasses import dataclass


@dataclass
class DummyToken:
    token: str


class DummyAzureTokenCredential():

    async def get_token(self, *args):
        return DummyToken(token="This is a dummy token")

    async def close(self, *args):
        pass
