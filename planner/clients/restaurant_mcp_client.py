import asyncio
import sys
from interfaces.mcp_client_interface import MCPClient


class RestaurantMCPClient(MCPClient):
    def __init__(self):
        super().__init__()
        self.client_name = "Restaurant"


async def main():
    if len(sys.argv) < 2:
        print(
            "Usage: uv run -m clients.restaurant_mcp_client servers/restaurant_mcp_server.py"
        )
        sys.exit(1)

    client = RestaurantMCPClient()
    try:
        await client.connect(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
