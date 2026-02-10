from typing import Any
from mcp.server.fastmcp import FastMCP
import datetime
import asyncio
from interfaces.mcp_server_interface import MCPServer
from data.transport_data import FLIGHT_DATA, TRAIN_DATA, PUBLIC_TRANSPORT_DATA
from utils.logger import get_logger
from utils.http_client import async_get
from config import TRANSPORT_MOCK_BOOL, TRANSPORT_API_BASE, TRANSPORT_API_KEY

logger = get_logger("TransportMCPServer")


class TransportMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("transport")
        self.USE_MOCK_DATA = TRANSPORT_MOCK_BOOL
        self.API_BASE = TRANSPORT_API_BASE
        self.API_KEY = TRANSPORT_API_KEY
        self.USER_AGENT = "transport-app/1.0"
        self.MOCK_FLIGHTS = FLIGHT_DATA
        self.MOCK_TRAINS = TRAIN_DATA
        self.MOCK_PUBLIC_TRANSPORT = PUBLIC_TRANSPORT_DATA
        logger.info(f"TransportMCPServer initialized | mock_mode={self.USE_MOCK_DATA}")

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def search_flights(
            origin: str, destination: str, date: str = None
        ) -> str:
            logger.info(f"search_flights | {origin} -> {destination} | date={date}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            params = {
                "origin": origin,
                "destination": destination,
                "date": date or str(datetime.date.today()),
            }
            data = await self.make_transport_request(
                f"{self.API_BASE}/flights/search", params
            )
            if not data or "flights" not in data:
                logger.warning(f"No flights found for {origin} -> {destination}")
                return f"No flights found.{mock_indicator}"
            result = "\n---\n".join([self.format_flight(f) for f in data["flights"]])
            logger.info(f"search_flights returned {len(data['flights'])} flights")
            return result

        @self.mcp.tool()
        async def search_trains(origin: str, destination: str, date: str = None) -> str:
            logger.info(f"search_trains | {origin} -> {destination} | date={date}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            params = {
                "origin": origin,
                "destination": destination,
                "date": date or str(datetime.date.today()),
            }
            data = await self.make_transport_request(
                f"{self.API_BASE}/trains/search", params
            )
            if not data or "trains" not in data:
                return f"No trains found.{mock_indicator}"
            return "\n---\n".join([self.format_train(t) for t in data["trains"]])

        @self.mcp.tool()
        async def search_public_transport(latitude: float, longitude: float) -> str:
            logger.info(f"search_public_transport | lat={latitude}, lon={longitude}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_transport_request(
                f"{self.API_BASE}/public/search",
                {"latitude": latitude, "longitude": longitude},
            )
            if not data or "public_transport" not in data:
                return f"No public transport found.{mock_indicator}"
            return "\n---\n".join(
                [self.format_public(p) for p in data["public_transport"]]
            )

        @self.mcp.tool()
        async def get_transport_details(option_id: str) -> str:
            logger.info(f"get_transport_details | id={option_id}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_transport_request(
                f"{self.API_BASE}/details", {"id": option_id}
            )
            if not data:
                return f"No details for {option_id}.{mock_indicator}"
            if "airline" in data:
                return self.format_flight(data)
            if "train" in data:
                return self.format_train(data)
            if "type" in data:
                return self.format_public(data)
            return f"Unknown transport type.{mock_indicator}"

    def start(self) -> None:
        logger.info("Starting Transport MCP Server")
        asyncio.run(self.register_tools())
        self.mcp.run(transport="stdio")

    async def make_transport_request(
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
            logger.error(f"Transport API failed | error={data['error']}")
            return None
        return data

    def get_mock_response(self, url: str, params: dict = None) -> dict[str, Any] | None:
        if "/flights/search" in url:
            return {"flights": self.MOCK_FLIGHTS}
        elif "/trains/search" in url:
            return {"trains": self.MOCK_TRAINS}
        elif "/public/search" in url:
            return {"public_transport": self.MOCK_PUBLIC_TRANSPORT}
        elif "/details" in url:
            for opt in (
                self.MOCK_FLIGHTS + self.MOCK_TRAINS + self.MOCK_PUBLIC_TRANSPORT
            ):
                if opt["id"] == params.get("id"):
                    return opt
        return None

    def format_flight(self, f: dict) -> str:
        return f"Flight {f['id']} | {f['airline']} | {f['from']} -> {f['to']} | Dep: {f['departure']} | Arr: {f['arrival']} | {f['duration']} | {f['price']} {f['currency']}"

    def format_train(self, t: dict) -> str:
        return f"Train {t['id']} | {t['train']} | {t['from']} -> {t['to']} | Dep: {t['departure']} | Arr: {t['arrival']} | {t['duration']} | {t['price']} {t['currency']}"

    def format_public(self, p: dict) -> str:
        return f"Public {p['id']} | {p['type']} | Route: {p['route']} | {p['location']} | {p['frequency']} | {p['price']} {p['currency']}"


if __name__ == "__main__":
    server = TransportMCPServer()
    server.start()
