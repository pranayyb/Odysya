import asyncio
import logging
from clients.restaurant_mcp_client import RestaurantMCPClient
from interfaces.tool_interface import AgentToolInterface

logger = logging.getLogger("Restaurant Tools")


class RestaurantTools(AgentToolInterface):
    def __init__(self, server_path: str = "servers.restaurant_mcp_server"):
        self.server_path = server_path
        self.client = RestaurantMCPClient()

    async def run(self, query: str) -> str:
        try:
            await self.client.connect(self.server_path)
            result = await self.client.process_query(query)
            return result
        except Exception as e:
            logger.error(f"Error running RestaurantTools query: {e}")
            return f"Error: {e}"
        finally:
            await self.client.cleanup()


