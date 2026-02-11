import asyncio
from clients.attraction_mcp_client import AttractionMCPClient
from interfaces.tool_interface import AgentToolInterface
from utils.logger import get_logger
from utils.error_handler import ToolError

logger = get_logger("AttractionTools")


class AttractionTools(AgentToolInterface):
    def __init__(self, server_path: str = "servers.attraction_mcp_server"):
        self.server_path = server_path
        self.client = AttractionMCPClient()
        logger.info(f"AttractionTools initialized | server={server_path}")

    async def run(self, query: str) -> str:
        logger.info(f"AttractionTools.run | query={query[:80]}...")
        try:
            await self.client.connect(self.server_path)
            result = await self.client.process_query(query)
            logger.info(f"AttractionTools.run completed | result_len={len(result)}")
            return result
        except Exception as e:
            logger.error(f"AttractionTools.run failed | error={e}")
            raise ToolError(str(e), tool_name="AttractionTools")
        finally:
            await self.client.cleanup()
