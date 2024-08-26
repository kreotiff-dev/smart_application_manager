import aiohttp


class HTTPClientAdapter:
    def __init__(self, config):
        self.config = config
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def post(self, url, **kwargs):
        if not self.session:
            self.session = aiohttp.ClientSession()
        async with self.session.post(url, **kwargs) as response:
            return await response.json()
