from typing import Any, Dict
import httpx
from mcp.server.fastmcp import FastMCP
import logging
import random
import asyncio
from interfaces.mcp_server_interface import MCPServer
from data import restaurant_data


class RestaurantMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("restaurant")
        self.USE_MOCK_DATA = True
        self.YELP_API_BASE = "https://api.yelp.com/v3"
        self.YELP_API_KEY = "YELP_API_KEY"
        self.USER_AGENT = "restaurant-app/1.0"
        self.MOCK_RESTAURANTS = restaurant_data

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def search_restaurants(
            location: str, term: str = "food", limit: int = 5
        ) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.YELP_API_BASE}/businesses/search"
            params = {"location": location, "term": term, "limit": limit}

            data = await self.make_yelp_request(url, params)
            if not data or "businesses" not in data:
                return f"No restaurants found for {location}.{mock_indicator}"

            restaurants = data["businesses"]
            formatted = [self.format_restaurant(r) for r in restaurants]
            return f"Restaurants in {location}{mock_indicator}:\n" + "\n---\n".join(
                formatted
            )

        @self.mcp.tool()
        async def get_restaurant_details(rest_id: str) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.YELP_API_BASE}/businesses/{rest_id}"
            data = await self.make_yelp_request(url)
            if not data:
                return f"Unable to fetch details for {rest_id}.{mock_indicator}"
            return self.format_restaurant(data)

        @self.mcp.tool()
        async def search_restaurants_by_coordinates(
            latitude: float, longitude: float, term: str = "food", limit: int = 5
        ) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.YELP_API_BASE}/businesses/search"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "term": term,
                "limit": limit,
            }
            data = await self.make_yelp_request(url, params)
            if not data or "businesses" not in data:
                return f"No restaurants found near coordinates ({latitude}, {longitude}).{mock_indicator}"
            restaurants = data["businesses"]
            formatted = [self.format_restaurant(r) for r in restaurants]
            return (
                f"Restaurants near ({latitude}, {longitude}){mock_indicator}:\n"
                + "\n---\n".join(formatted)
            )

        @self.mcp.tool()
        async def toggle_mock_mode(enable_mock: bool = True) -> str:
            return self.toggle_mock_mode(enable_mock)

    async def handle_request(self, tool_name: str, params: Dict[str, Any]) -> Any:
        try:
            return await self.mcp.call_tool(tool_name, params)
        except Exception as e:
            logging.error(f"Error handling request {tool_name}: {e}")
            return {"error": str(e)}

    def toggle_mock_mode(self, enable_mock: bool) -> str:
        self.USE_MOCK_DATA = enable_mock
        mode = "MOCK DATA" if self.USE_MOCK_DATA else "REAL API"
        return f"Restaurant Server mode switched to: {mode}"

    def start(self) -> None:
        logging.info("Starting Restaurant MCP Server")
        logging.info(f"Mock mode enabled: {self.USE_MOCK_DATA}")
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
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, headers=headers, params=params, timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logging.error(f"Yelp API request failed: {e}")
                return None

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
        name = res.get("name", "Unknown")
        rating = res.get("rating", "N/A")
        price = res.get("price", "N/A")
        category = res.get("categories", [{}])[0].get("title", "General")
        address = res.get("location", {}).get("address1", "Unknown")
        city = res.get("location", {}).get("city", "")
        phone = res.get("phone", "N/A")

        return f"""
        Restaurant: {name}
        Category: {category}
        Rating: {rating} stars
        Price: {price}
        Address: {address}, {city}
        Phone: {phone}
        ID: {res.get("id", "N/A")}
        """


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    server = RestaurantMCPServer()
    server.start()
