import asyncio
import logging
from clients.hotel_mcp_client import HotelMCPClient
from interfaces.tool_interface import AgentToolInterface

logger = logging.getLogger("Hotel Tools")


class HotelTools(AgentToolInterface):
    def __init__(self, server_path: str = "servers.hotel_mcp_server"):
        self.server_path = server_path
        self.client = HotelMCPClient()

    async def run(self, query: str) -> str:
        try:
            await self.client.connect(self.server_path)
            result = await self.client.process_query(query)
            return result
        except Exception as e:
            logger.error(f"Error running HotelTools query: {e}")
            return f"Error: {e}"
        finally:
            await self.client.cleanup()
