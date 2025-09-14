from typing import Any, Dict
import httpx
from mcp.server.fastmcp import FastMCP
import logging
import asyncio
from interfaces.mcp_server_interface import MCPServer
from data.weather_data import WEATHER_DATA
from config import WEATHER_MOCK_BOOL


class WeatherMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("weather")
        self.USE_MOCK_DATA = WEATHER_MOCK_BOOL
        self.API_BASE = "https://api.openweathermap.org/data/2.5"
        self.API_KEY = "YOUR_OPENWEATHER_API_KEY"
        self.USER_AGENT = "weather-app/1.0"
        self.MOCK_WEATHER = WEATHER_DATA

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def get_current_weather(city: str) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            params = {"q": city, "units": "metric"}
            data = await self.make_weather_request("weather", params)
            if not data:
                return f"No weather data available for {city}.{mock_indicator}"
            return self.format_current_weather(data) + mock_indicator

        @self.mcp.tool()
        async def get_weather_forecast(city: str, days: int = 3) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            params = {"q": city, "cnt": days}
            data = await self.make_weather_request("forecast", params)
            if not data:
                return f"No forecast data available for {city}.{mock_indicator}"
            return self.format_forecast(data) + mock_indicator

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
        return f"Weather Server mode switched to: {mode}"

    def start(self) -> None:
        logging.info("Starting Weather MCP Server")
        logging.info(f"Mock mode enabled: {self.USE_MOCK_DATA}")
        asyncio.run(self.register_tools())
        self.mcp.run(transport="stdio")

    async def make_weather_request(
        self, endpoint: str, params: dict = None
    ) -> dict[str, Any] | None:
        if self.USE_MOCK_DATA:
            return self.get_mock_response(endpoint, params)

        url = f"{self.API_BASE}/{endpoint}"
        headers = {"User-Agent": self.USER_AGENT}
        params = params or {}
        params["appid"] = self.API_KEY
        params["units"] = "metric"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, headers=headers, params=params, timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logging.error(f"Weather API request failed: {e}")
                return None

    def get_mock_response(
        self, endpoint: str, params: dict = None
    ) -> dict[str, Any] | None:
        city = params.get("q", "").lower() if params else ""
        if endpoint == "weather" and city in self.MOCK_WEATHER:
            return self.MOCK_WEATHER[city]
        elif endpoint == "forecast" and city in self.MOCK_WEATHER:
            base = self.MOCK_WEATHER[city]
            return {
                "city": base["city"],
                "forecast": [
                    {
                        "day": "Day 1",
                        "temp": base["temp"],
                        "condition": base["condition"],
                    },
                    {
                        "day": "Day 2",
                        "temp": base["temp"] + 1,
                        "condition": "Partly Cloudy",
                    },
                    {"day": "Day 3", "temp": base["temp"] - 2, "condition": "Rainy"},
                ],
            }
        return None

    def format_current_weather(self, data: dict) -> str:
        return f"""
        Weather in {data['city']}
        Condition: {data['condition']}
        Temperature: {data['temp']}°C (Feels like {data['feels_like']}°C)
        Humidity: {data['humidity']}%
        Wind: {data['wind']} km/h
        """

    def format_forecast(self, data: dict) -> str:
        lines = [f"Weather Forecast for {data['city']}:"]
        for d in data["forecast"]:
            lines.append(f"- {d['day']}: {d['temp']}°C, {d['condition']}")
        return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    server = WeatherMCPServer()
    server.start()
