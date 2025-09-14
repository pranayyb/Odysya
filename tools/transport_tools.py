import asyncio
import logging
from clients.transport_mcp_client import TransportMCPClient
from interfaces.tool_interface import AgentToolInterface

logger = logging.getLogger("Weather Tools")


class TransportTools(AgentToolInterface):
    def __init__(self, server_path: str = "servers.transport_mcp_server"):
        self.server_path = server_path
        self.client = TransportMCPClient()

    async def run(self, query: str) -> str:
        try:
            await self.client.connect(self.server_path)
            result = await self.client.process_query(query)
            return result
        except Exception as e:
            logger.error(f"Error running TransportTools query: {e}")
            return f"Error: {e}"
        finally:
            await self.client.cleanup()
