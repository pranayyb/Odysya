import asyncio
from typing import Any, Dict
import httpx
from mcp.server.fastmcp import FastMCP
import logging
import datetime

from interfaces.mcp_server_interface import MCPServer


class EventMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("events")
        self.EVENTS_API_BASE = "https://events-api.example.com/v1"
        self.API_KEY = "YOUR_EVENTS_API_KEY"
        self.USER_AGENT = "events-app/1.0"
        self.MOCK_EVENTS = [
            {
                "id": "evt_101",
                "name": "Coldplay Live Concert",
                "type": "Concert",
                "location": "Wembley Stadium, New York",
                "date": "2025-12-05",
                "time": "19:00",
                "price": 120.00,
                "currency": "GBP",
                "organizer": "Live Nation",
            },
            {
                "id": "evt_102",
                "name": "Paris Fashion Week",
                "type": "Exhibition",
                "location": "Grand Palais, Paris",
                "date": "2025-12-10",
                "time": "10:00",
                "price": 0.00,
                "currency": "EUR",
                "organizer": "Paris Fashion Council",
            },
            {
                "id": "evt_103",
                "name": "Tokyo Anime Festival",
                "type": "Festival",
                "location": "Tokyo Big Sight",
                "date": "2025-12-15",
                "time": "09:00",
                "price": 50.00,
                "currency": "JPY",
                "organizer": "Anime Japan",
            },
        ]
        self.USE_MOCK_DATA = True

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def search_events(
            city: str, start_date: str = None, end_date: str = None
        ) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.EVENTS_API_BASE}/events/search"
            params = {"city": city, "start_date": start_date, "end_date": end_date}

            data = await self.make_events_request(url, params)
            if not data or "events" not in data or len(data["events"]) == 0:
                return f"No events found in {city}.{mock_indicator}"

            events = data["events"]
            return f"Events in {city}{mock_indicator}:\n" + "\n---\n".join(
                [self.format_event(e) for e in events]
            )

        @self.mcp.tool()
        async def get_event_details(event_id: str) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.EVENTS_API_BASE}/events/details"
            params = {"id": event_id}

            data = await self.make_events_request(url, params)
            if not data:
                return f"No details available for event {event_id}.{mock_indicator}"

            return self.format_event(data)

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
        return f"Event Server mode switched to: {mode}"

    def start(self) -> None:
        logging.info("Starting Event MCP Server")
        logging.info(f"Mock mode enabled: {self.USE_MOCK_DATA}")
        asyncio.run(self.register_tools())
        self.mcp.run(transport="stdio")

    async def make_events_request(
        self, url: str, params: dict = None
    ) -> dict[str, Any] | None:
        if self.USE_MOCK_DATA:
            return self.get_mock_response(url, params)

        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
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
                logging.error(f"Events API request failed: {e}")
                return None

    def get_mock_response(self, url: str, params: dict = None) -> dict[str, Any] | None:
        if "/events/search" in url:
            city = params.get("city")
            return {
                "events": [
                    e for e in self.MOCK_EVENTS if city.lower() in e["location"].lower()
                ]
            }
        elif "/events/details" in url:
            for e in self.MOCK_EVENTS:
                if e["id"] == params.get("id"):
                    return e
        return None

    def format_event(self, e: dict) -> str:
        return f"""
        Event {e['id']}
        Name: {e['name']}
        Type: {e['type']}
        Location: {e['location']}
        Date: {e['date']} | Time: {e['time']}
        Organizer: {e['organizer']}
        Price: {e['price']} {e['currency']}
        """


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    server = EventMCPServer()
    server.start()
