import asyncio
import sys
from interfaces.mcp_client_interface import MCPClient
from utils.logger import get_logger

logger = get_logger("EventMCPClient")


class EventMCPClient(MCPClient):
    def __init__(self):
        super().__init__()
        self.client_name = "Event"
        logger.info("EventMCPClient initialized")


async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run -m clients.event_mcp_client servers/event_mcp_server.py")
        sys.exit(1)

    client = EventMCPClient()
    try:
        await client.connect(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
