import asyncio
from typing import Any
from mcp.server.fastmcp import FastMCP
from data.attractions_data import ATTRACTIONS_DATA
from interfaces.mcp_server_interface import MCPServer
from utils.logger import get_logger
from utils.http_client import async_get
from config import ATTRACTION_MOCK_BOOL, ATTRACTION_API_BASE, ATTRACTION_API_KEY

logger = get_logger("AttractionMCPServer")


class AttractionMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("attractions")
        self.ATTRACTION_API_BASE = ATTRACTION_API_BASE
        self.API_KEY = ATTRACTION_API_KEY
        self.USER_AGENT = "attractions-app/1.0"
        self.MOCK_ATTRACTIONS = ATTRACTIONS_DATA
        self.USE_MOCK_DATA = ATTRACTION_MOCK_BOOL
        logger.info(f"AttractionMCPServer initialized | mock_mode={self.USE_MOCK_DATA}")

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def search_attractions(
            city: str, category: str = None
        ) -> str:
            logger.info(
                f"search_attractions | city={city} | category={category}"
            )
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_attraction_request(
                f"{self.ATTRACTION_API_BASE}/attractions/search",
                {"city": city, "category": category},
            )
            if not data or "attractions" not in data or len(data["attractions"]) == 0:
                logger.warning(f"No tourist attractions found in {city}")
                return f"No tourist attractions found in {city}.{mock_indicator}"
            attractions = data["attractions"]
            logger.info(f"search_attractions returned {len(attractions)} attractions for {city}")
            return f"Tourist attractions in {city}{mock_indicator}:\n" + "\n---\n".join(
                [self.format_attraction(a) for a in attractions]
            )

        @self.mcp.tool()
        async def get_attraction_details(attraction_id: str) -> str:
            logger.info(f"get_attraction_details | attraction_id={attraction_id}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_attraction_request(
                f"{self.ATTRACTION_API_BASE}/attractions/details", {"id": attraction_id}
            )
            if not data:
                return f"No details for attraction {attraction_id}.{mock_indicator}"
            return self.format_attraction(data)

    def start(self) -> None:
        logger.info("Starting Attraction MCP Server")
        asyncio.run(self.register_tools())
        self.mcp.run(transport="stdio")

    async def make_attraction_request(
        self, url: str, params: dict = None
    ) -> dict[str, Any] | None:
        if self.USE_MOCK_DATA:
            return self.get_mock_response(url, params)
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "User-Agent": self.USER_AGENT,
        }
        data = await async_get(url, params=params, headers=headers)
        if "error" in data:
            logger.error(f"Attraction API failed | url={url} | error={data['error']}")
            return None
        return data

    def get_mock_response(self, url: str, params: dict = None) -> dict[str, Any] | None:
        if "/attractions/search" in url:
            city = params.get("city", "")
            category = params.get("category")
            filtered = [
                a for a in self.MOCK_ATTRACTIONS if city.lower() in a["city"].lower()
            ]
            if category:
                filtered = [
                    a for a in filtered if category.lower() in a["type"].lower()
                ]
            return {"attractions": filtered}
        elif "/attractions/details" in url:
            for a in self.MOCK_ATTRACTIONS:
                if a["id"] == params.get("id"):
                    return a
        return None

    def format_attraction(self, a: dict) -> str:
        fee = f"{a['entry_fee']} {a['currency']}" if a.get("entry_fee") else "Free"
        if a.get("entry_fee") == 0:
            fee = "Free"
        return (
            f"Attraction {a['id']} | {a['name']} | Type: {a['type']} | "
            f"Location: {a['location']} | Rating: {a.get('rating', 'N/A')}/5 | "
            f"Entry Fee: {fee} | Timings: {a.get('timings', 'N/A')} | "
            f"Description: {a.get('description', '')}"
        )


if __name__ == "__main__":
    server = AttractionMCPServer()
    server.start()
