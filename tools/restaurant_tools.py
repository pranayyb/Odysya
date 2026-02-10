import asyncio
from clients.restaurant_mcp_client import RestaurantMCPClient
from interfaces.tool_interface import AgentToolInterface
from utils.logger import get_logger
from utils.error_handler import ToolError

logger = get_logger("RestaurantTools")


class RestaurantTools(AgentToolInterface):
    def __init__(self, server_path: str = "servers.restaurant_mcp_server"):
        self.server_path = server_path
        self.client = RestaurantMCPClient()
        logger.info(f"RestaurantTools initialized | server={server_path}")

    async def run(self, query: str) -> str:
        logger.info(f"RestaurantTools.run | query={query[:80]}...")
        try:
            await self.client.connect(self.server_path)
            result = await self.client.process_query(query)
            logger.info(f"RestaurantTools.run completed | result_len={len(result)}")
            return result
        except Exception as e:
            logger.error(f"RestaurantTools.run failed | error={e}")
            raise ToolError(str(e), tool_name="RestaurantTools")
        finally:
            await self.client.cleanup()
