from typing import Any
from mcp.server.fastmcp import FastMCP
import random
import asyncio
from interfaces.mcp_server_interface import MCPServer
from data.restaurant_data import RESTAURANT_DATA
from utils.logger import get_logger
from utils.http_client import async_get
from config import RESTAURANT_MOCK_BOOL, YELP_API_BASE, YELP_API_KEY

logger = get_logger("RestaurantMCPServer")


class RestaurantMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("restaurant")
        self.USE_MOCK_DATA = RESTAURANT_MOCK_BOOL
        self.YELP_API_BASE = YELP_API_BASE
        self.YELP_API_KEY = YELP_API_KEY
        self.USER_AGENT = "restaurant-app/1.0"
        self.MOCK_RESTAURANTS = RESTAURANT_DATA
        logger.info(f"RestaurantMCPServer initialized | mock_mode={self.USE_MOCK_DATA}")

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def search_restaurants(
            location: str, term: str = "food", limit: int = 5
        ) -> str:
            logger.info(f"search_restaurants | location={location} | term={term}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_yelp_request(
                f"{self.YELP_API_BASE}/businesses/search",
                {"location": location, "term": term, "limit": limit},
            )
            if not data or "businesses" not in data:
                logger.warning(f"No restaurants found for {location}")
                return f"No restaurants found for {location}.{mock_indicator}"
            restaurants = data["businesses"]
            logger.info(
                f"search_restaurants returned {len(restaurants)} results for {location}"
            )
            return f"Restaurants in {location}{mock_indicator}:\n" + "\n---\n".join(
                [self.format_restaurant(r) for r in restaurants]
            )

        @self.mcp.tool()
        async def get_restaurant_details(rest_id: str) -> str:
            logger.info(f"get_restaurant_details | rest_id={rest_id}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_yelp_request(
                f"{self.YELP_API_BASE}/businesses/{rest_id}"
            )
            if not data:
                return f"Unable to fetch details for {rest_id}.{mock_indicator}"
            return self.format_restaurant(data)

        @self.mcp.tool()
        async def search_restaurants_by_coordinates(
            latitude: float, longitude: float, term: str = "food", limit: int = 5
        ) -> str:
            logger.info(
                f"search_restaurants_by_coordinates | lat={latitude}, lon={longitude}"
            )
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_yelp_request(
                f"{self.YELP_API_BASE}/businesses/search",
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "term": term,
                    "limit": limit,
                },
            )
            if not data or "businesses" not in data:
                return f"No restaurants found near ({latitude}, {longitude}).{mock_indicator}"
            return (
                f"Restaurants near ({latitude}, {longitude}){mock_indicator}:\n"
                + "\n---\n".join(
                    [self.format_restaurant(r) for r in data["businesses"]]
                )
            )

    def start(self) -> None:
        logger.info("Starting Restaurant MCP Server")
        asyncio.run(self.register_tools())
        self.mcp.run(transport="stdio")

    async def make_yelp_request(
        self, url: str, params: dict = None
    ) -> dict[str, Any] | None:
        if self.USE_MOCK_DATA:
            return self.get_mock_response(url, params)
        headers = {
            "Authorization": f"Bearer {self.YELP_API_KEY}",
            "User-Agent": self.USER_AGENT,
        }
        data = await async_get(url, params=params, headers=headers)
        if "error" in data:
            logger.error(f"Yelp API failed | error={data['error']}")
            return None
        return data

    def get_mock_response(self, url: str, params: dict = None) -> dict[str, Any] | None:
        if "/businesses/search" in url:
            results = []
            for res in self.MOCK_RESTAURANTS:
                r = res.copy()
                r["rating"] = round(r["rating"] + random.uniform(-0.2, 0.2), 1)
                results.append(r)
            return {"businesses": results}
        elif "/businesses/" in url:
            rest_id = url.split("/")[-1]
            for res in self.MOCK_RESTAURANTS:
                if res["id"] == rest_id:
                    return res
            return {
                "id": rest_id,
                "name": "Mock Restaurant",
                "rating": 4.0,
                "location": {"address1": "Mock St", "city": "Test City"},
            }
        return None

    def format_restaurant(self, res: dict) -> str:
        return f"Restaurant: {res.get('name', 'Unknown')} | {res.get('categories', [{}])[0].get('title', 'General')} | Rating: {res.get('rating', 'N/A')} | Price: {res.get('price', 'N/A')} | {res.get('location', {}).get('address1', 'N/A')}, {res.get('location', {}).get('city', '')} | Phone: {res.get('phone', 'N/A')} | ID: {res.get('id', 'N/A')}"


if __name__ == "__main__":
    server = RestaurantMCPServer()
    server.start()
