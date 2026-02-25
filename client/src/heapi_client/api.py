import requests
from requests.exceptions import RequestException, Timeout


class API:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str):
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Timeout:
            raise RuntimeError(f"GET request to {url} timed out")
        except RequestException as e:
            raise RuntimeError(f"GET request to {url} failed: {str(e)}")