import aiohttp
import traceback

class AioHttpCalls:
    def __init__(
                 self,
                 config,
                 logger,
                 timeout = 10
                 ):
                 
        self.prometheus_url = config.validator.prometheus_metrics_url
        self.logger = logger
        self.timeout = timeout

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()
    
    async def handle_prometheus_request(self, url, callback):
        try:
            async with self.session.get(url, timeout=self.timeout) as response:
                
                if 200 <= response.status < 300:
                    data = await callback(response.text())
                    return data
                
                else:
                    self.logger.warning(f"Request to {url} failed with status code {response.status}")
                    return None
                
        except aiohttp.ClientError as e:
            self.logger.error(f"Issue with making request to {url}: {e}")
            return None
        
        except TimeoutError as e:
            self.logger.error(f"Issue with making request to {url}. TimeoutError: {e}")
            return None

        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            traceback.print_exc()
            return None

    async def fetch_prometheus_metrics(self) -> str:
        url = self.prometheus_url

        async def process_response(response):
            data = await response
            return data
        return await self.handle_prometheus_request(url, process_response)