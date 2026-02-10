import asyncio
from clients.hotel_mcp_client import HotelMCPClient
from interfaces.tool_interface import AgentToolInterface
from utils.logger import get_logger
from utils.error_handler import ToolError

logger = get_logger("HotelTools")


class HotelTools(AgentToolInterface):
    def __init__(self, server_path: str = "servers.hotel_mcp_server"):
        self.server_path = server_path
        self.client = HotelMCPClient()
        logger.info(f"HotelTools initialized | server={server_path}")

    async def run(self, query: str) -> str:
        logger.info(f"HotelTools.run | query={query[:80]}...")
        try:
            await self.client.connect(self.server_path)
            result = await self.client.process_query(query)
            logger.info(f"HotelTools.run completed | result_len={len(result)}")
            return result
        except Exception as e:
            logger.error(f"HotelTools.run failed | error={e}")
            raise ToolError(str(e), tool_name="HotelTools")
        finally:
            await self.client.cleanup()
