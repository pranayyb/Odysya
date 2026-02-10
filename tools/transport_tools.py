import asyncio
from clients.transport_mcp_client import TransportMCPClient
from interfaces.tool_interface import AgentToolInterface
from utils.logger import get_logger
from utils.error_handler import ToolError

logger = get_logger("TransportTools")


class TransportTools(AgentToolInterface):
    def __init__(self, server_path: str = "servers.transport_mcp_server"):
        self.server_path = server_path
        self.client = TransportMCPClient()
        logger.info(f"TransportTools initialized | server={server_path}")

    async def run(self, query: str) -> str:
        logger.info(f"TransportTools.run | query={query[:80]}...")
        try:
            await self.client.connect(self.server_path)
            result = await self.client.process_query(query)
            logger.info(f"TransportTools.run completed | result_len={len(result)}")
            return result
        except Exception as e:
            logger.error(f"TransportTools.run failed | error={e}")
            raise ToolError(str(e), tool_name="TransportTools")
        finally:
            await self.client.cleanup()
