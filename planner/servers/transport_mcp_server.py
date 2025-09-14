from typing import Any, Dict
import httpx
from mcp.server.fastmcp import FastMCP
import logging
import datetime
import asyncio
from interfaces.mcp_server_interface import MCPServer
from data.transport_data import flight_data
from data.transport_data import train_data
from data.transport_data import public_transport_data


class TransportMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("transport")
        self.USE_MOCK_DATA = True
        self.API_BASE = "https://transport-api.example.com/v1"
        self.API_KEY = "YOUR_TRANSPORT_API_KEY"
        self.USER_AGENT = "transport-app/1.0"
        self.MOCK_FLIGHTS = flight_data
        self.MOCK_TRAINS = train_data
        self.MOCK_PUBLIC_TRANSPORT = public_transport_data

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def search_flights(
            origin: str, destination: str, date: str = None
        ) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.API_BASE}/flights/search"
            params = {
                "origin": origin,
                "destination": destination,
                "date": date or str(datetime.date.today()),
            }
            data = await self.make_transport_request(url, params)
            if not data or "flights" not in data:
                return f"No flights found.{mock_indicator}"
            return "\n---\n".join([self.format_flight(f) for f in data["flights"]])

        @self.mcp.tool()
        async def search_trains(origin: str, destination: str, date: str = None) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.API_BASE}/trains/search"
            params = {
                "origin": origin,
                "destination": destination,
                "date": date or str(datetime.date.today()),
            }
            data = await self.make_transport_request(url, params)
            if not data or "trains" not in data:
                return f"No trains found.{mock_indicator}"
            return "\n---\n".join([self.format_train(t) for t in data["trains"]])

        @self.mcp.tool()
        async def search_public_transport(latitude: float, longitude: float) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.API_BASE}/public/search"
            params = {"latitude": latitude, "longitude": longitude}
            data = await self.make_transport_request(url, params)
            if not data or "public_transport" not in data:
                return f"No public transport found.{mock_indicator}"
            return "\n---\n".join(
                [self.format_public(p) for p in data["public_transport"]]
            )

        @self.mcp.tool()
        async def get_transport_details(option_id: str) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.API_BASE}/details"
            params = {"id": option_id}
            data = await self.make_transport_request(url, params)
            if not data:
                return f"No details for {option_id}.{mock_indicator}"
            if "airline" in data:
                return self.format_flight(data)
            if "train" in data:
                return self.format_train(data)
            if "type" in data:
                return self.format_public(data)
            return f"Unknown transport type.{mock_indicator}"

        @self.mcp.tool()
        async def toggle_mock_mode(enable_mock: bool = True) -> str:
            return self.toggle_mock_mode(enable_mock)

    async def handle_request(self, tool_name: str, params: Dict[str, Any]) -> Any:
        try:
            return await self.mcp.call_tool(tool_name, params)
        except Exception as e:
            logging.error(f"Error: {e}")
            return {"error": str(e)}

    def toggle_mock_mode(self, enable_mock: bool) -> str:
        self.USE_MOCK_DATA = enable_mock
        mode = "MOCK DATA" if self.USE_MOCK_DATA else "REAL API"
        return f"Transport Server mode switched to: {mode}"

    def start(self) -> None:
        logging.info("Starting Transport MCP Server")
        logging.info(f"Mock mode enabled: {self.USE_MOCK_DATA}")
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
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, headers=headers, params=params, timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logging.error(f"Transport API failed: {e}")
                return None

    def get_mock_response(self, url: str, params: dict = None) -> dict[str, Any] | None:
        if "/flights/search" in url:
            return {"flights": self.MOCK_FLIGHTS}
        elif "/trains/search" in url:
            return {"trains": self.MOCK_TRAINS}
        elif "/public/search" in url:
            return {"public_transport": self.MOCK_PUBLIC_TRANSPORT}
        elif "/details" in url:
            all_options = (
                self.MOCK_FLIGHTS + self.MOCK_TRAINS + self.MOCK_PUBLIC_TRANSPORT
            )
            for opt in all_options:
                if opt["id"] == params.get("id"):
                    return opt
        return None

    def format_flight(self, f: dict) -> str:
        return f"""
        ✈️ Flight {f['id']}
        Airline: {f['airline']}
        From: {f['from']} → To: {f['to']}
        Departure: {f['departure']} | Arrival: {f['arrival']}
        Duration: {f['duration']}
        Price: {f['price']} {f['currency']}
        """

    def format_train(self, t: dict) -> str:
        return f"""
        🚆 Train {t['id']}
        Train: {t['train']}
        From: {t['from']} → To: {t['to']}
        Departure: {t['departure']} | Arrival: {t['arrival']}
        Duration: {t['duration']}
        Price: {t['price']} {t['currency']}
        """

    def format_public(self, p: dict) -> str:
        return f"""
        🚌 Public Transport {p['id']}
        Type: {p['type']}
        Route: {p['route']}
        Location: {p['location']}
        Frequency: {p['frequency']}
        Price: {p['price']} {p['currency']}
        """


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    server = TransportMCPServer()
    server.start()
