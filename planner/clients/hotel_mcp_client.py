import asyncio
import sys
from interfaces.mcp_client_interface import MCPClient


class HotelMCPClient(MCPClient):
    def __init__(self):
        super().__init__()
        self.client_name = "Hotel"


async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run -m clients.hotel_mcp_client servers/hotel_mcp_server.py")
        sys.exit(1)

    client = HotelMCPClient()
    try:
        await client.connect(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
