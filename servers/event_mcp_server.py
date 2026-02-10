import asyncio
from typing import Any
from mcp.server.fastmcp import FastMCP
from data.events_data import EVENTS_DATA
from interfaces.mcp_server_interface import MCPServer
from utils.logger import get_logger
from utils.http_client import async_get
from config import EVENT_MOCK_BOOL, EVENTS_API_BASE, EVENTS_API_KEY

logger = get_logger("EventMCPServer")


class EventMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("events")
        self.EVENTS_API_BASE = EVENTS_API_BASE
        self.API_KEY = EVENTS_API_KEY
        self.USER_AGENT = "events-app/1.0"
        self.MOCK_EVENTS = EVENTS_DATA
        self.USE_MOCK_DATA = EVENT_MOCK_BOOL
        logger.info(f"EventMCPServer initialized | mock_mode={self.USE_MOCK_DATA}")

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def search_events(
            city: str, start_date: str = None, end_date: str = None
        ) -> str:
            logger.info(
                f"search_events | city={city} | dates={start_date} to {end_date}"
            )
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_events_request(
                f"{self.EVENTS_API_BASE}/events/search",
                {"city": city, "start_date": start_date, "end_date": end_date},
            )
            if not data or "events" not in data or len(data["events"]) == 0:
                logger.warning(f"No events found in {city}")
                return f"No events found in {city}.{mock_indicator}"
            events = data["events"]
            logger.info(f"search_events returned {len(events)} events for {city}")
            return f"Events in {city}{mock_indicator}:\n" + "\n---\n".join(
                [self.format_event(e) for e in events]
            )

        @self.mcp.tool()
        async def get_event_details(event_id: str) -> str:
            logger.info(f"get_event_details | event_id={event_id}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_events_request(
                f"{self.EVENTS_API_BASE}/events/details", {"id": event_id}
            )
            if not data:
                return f"No details for event {event_id}.{mock_indicator}"
            return self.format_event(data)

    def start(self) -> None:
        logger.info("Starting Event MCP Server")
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
        data = await async_get(url, params=params, headers=headers)
        if "error" in data:
            logger.error(f"Events API failed | url={url} | error={data['error']}")
            return None
        return data

    def get_mock_response(self, url: str, params: dict = None) -> dict[str, Any] | None:
        if "/events/search" in url:
            city = params.get("city", "")
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
        return f"Event {e['id']} | {e['name']} | Type: {e['type']} | Location: {e['location']} | Date: {e['date']} {e['time']} | Organizer: {e['organizer']} | Price: {e['price']} {e['currency']}"


if __name__ == "__main__":
    server = EventMCPServer()
    server.start()
