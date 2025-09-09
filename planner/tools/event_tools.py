import asyncio
import logging
from clients.event_mcp_client import EventMCPClient
from interfaces.tool_interface import AgentToolInterface

logger = logging.getLogger("Event Tools")


class EventTools(AgentToolInterface):
    def __init__(self, server_path: str = "servers.event_mcp_server"):
        self.server_path = server_path
        self.client = EventMCPClient()

    async def run(self, query: str) -> str:
        try:
            await self.client.connect(self.server_path)
            result = await self.client.process_query(query)
            return result
        except Exception as e:
            logger.error(f"Error running EventTools query: {e}")
            return f"Error: {e}"
        finally:
            await self.client.cleanup()
