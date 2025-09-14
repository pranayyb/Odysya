import requests
import time
from utils.logger import get_logger

logger = get_logger("HTTPClient")


def get(url, params=None, headers=None, timeout=10):
    try:
        start = time.time()
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        latency = round(time.time() - start, 3)

        logger.info(f"GET {url} | status={response.status_code} | latency={latency}s")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"GET {url} | Timeout after {timeout}s")
        return {"error": "timeout"}
    except requests.exceptions.RequestException as e:
        logger.error(f"GET {url} | Failed: {e}")
        return {"error": str(e)}
