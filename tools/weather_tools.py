import asyncio
from clients.weather_mcp_client import WeatherMCPClient
from interfaces.tool_interface import AgentToolInterface
from utils.logger import get_logger
from utils.error_handler import ToolError

logger = get_logger("WeatherTools")


class WeatherTools(AgentToolInterface):
    def __init__(self, server_path: str = "servers.weather_mcp_server"):
        self.server_path = server_path
        self.client = WeatherMCPClient()
        logger.info(f"WeatherTools initialized | server={server_path}")

    async def run(self, query: str) -> str:
        logger.info(f"WeatherTools.run | query={query[:80]}...")
        try:
            await self.client.connect(self.server_path)
            result = await self.client.process_query(query)
            logger.info(f"WeatherTools.run completed | result_len={len(result)}")
            return result
        except Exception as e:
            logger.error(f"WeatherTools.run failed | error={e}")
            raise ToolError(str(e), tool_name="WeatherTools")
        finally:
            await self.client.cleanup()
