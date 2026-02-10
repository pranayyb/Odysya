import asyncio
from clients.event_mcp_client import EventMCPClient
from interfaces.tool_interface import AgentToolInterface
from utils.logger import get_logger
from utils.error_handler import ToolError

logger = get_logger("EventTools")


class EventTools(AgentToolInterface):
    def __init__(self, server_path: str = "servers.event_mcp_server"):
        self.server_path = server_path
        self.client = EventMCPClient()
        logger.info(f"EventTools initialized | server={server_path}")

    async def run(self, query: str) -> str:
        logger.info(f"EventTools.run | query={query[:80]}...")
        try:
            await self.client.connect(self.server_path)
            result = await self.client.process_query(query)
            logger.info(f"EventTools.run completed | result_len={len(result)}")
            return result
        except Exception as e:
            logger.error(f"EventTools.run failed | error={e}")
            raise ToolError(str(e), tool_name="EventTools")
        finally:
            await self.client.cleanup()
