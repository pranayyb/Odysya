import time
import httpx
import asyncio
from utils.logger import get_logger

logger = get_logger("HTTPClient")

DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5


async def async_get(
    url: str,
    params: dict = None,
    headers: dict = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=timeout
                )
            latency = round(time.time() - start, 3)

            logger.info(
                f"ASYNC GET {url} | status={response.status_code} | latency={latency}s | attempt={attempt}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(
                f"ASYNC GET {url} | attempt {attempt}/{MAX_RETRIES} failed: {e}"
            )
            if attempt < MAX_RETRIES:
                sleep_time = BACKOFF_FACTOR**attempt
                logger.info(f"Retrying in {sleep_time:.1f}s...")
                await asyncio.sleep(sleep_time)
            else:
                logger.error(
                    f"ASYNC GET {url} | All {MAX_RETRIES} attempts exhausted: {e}"
                )
                return {"error": str(e)}
