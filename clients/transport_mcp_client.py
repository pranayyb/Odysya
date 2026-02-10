import asyncio
import sys
from interfaces.mcp_client_interface import MCPClient
from utils.logger import get_logger

logger = get_logger("TransportMCPClient")


class TransportMCPClient(MCPClient):
    def __init__(self):
        super().__init__()
        self.client_name = "Transport"
        logger.info("TransportMCPClient initialized")


async def main():
    if len(sys.argv) < 2:
        print(
            "Usage: uv run -m clients.transport_mcp_client servers/transport_mcp_server.py"
        )
        sys.exit(1)

    client = TransportMCPClient()
    try:
        await client.connect(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
