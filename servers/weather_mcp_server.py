from typing import Any
from mcp.server.fastmcp import FastMCP
import asyncio
from interfaces.mcp_server_interface import MCPServer
from data.weather_data import WEATHER_DATA
from utils.logger import get_logger
from utils.http_client import async_get
from config import WEATHER_MOCK_BOOL, OPENWEATHER_API_BASE, OPENWEATHER_API_KEY

logger = get_logger("WeatherMCPServer")


class WeatherMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("weather")
        self.USE_MOCK_DATA = WEATHER_MOCK_BOOL
        self.API_BASE = OPENWEATHER_API_BASE
        self.API_KEY = OPENWEATHER_API_KEY
        self.USER_AGENT = "weather-app/1.0"
        self.MOCK_WEATHER = WEATHER_DATA
        logger.info(f"WeatherMCPServer initialized | mock_mode={self.USE_MOCK_DATA}")

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def get_current_weather(city: str) -> str:
            logger.info(f"get_current_weather | city={city}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_weather_request(
                "weather", {"q": city, "units": "metric"}
            )
            if not data:
                logger.warning(f"No weather data for {city}")
                return f"No weather data available for {city}.{mock_indicator}"
            logger.info(f"get_current_weather returned data for {city}")
            return self.format_current_weather(data) + mock_indicator

        @self.mcp.tool()
        async def get_weather_forecast(city: str, days: int = 3) -> str:
            logger.info(f"get_weather_forecast | city={city} | days={days}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            data = await self.make_weather_request("forecast", {"q": city, "cnt": days})
            if not data:
                return f"No forecast data for {city}.{mock_indicator}"
            logger.info(f"get_weather_forecast returned data for {city}")
            return self.format_forecast(data) + mock_indicator

    def start(self) -> None:
        logger.info("Starting Weather MCP Server")
        asyncio.run(self.register_tools())
        self.mcp.run(transport="stdio")

    async def make_weather_request(
        self, endpoint: str, params: dict = None
    ) -> dict[str, Any] | None:
        if self.USE_MOCK_DATA:
            return self.get_mock_response(endpoint, params)
        url = f"{self.API_BASE}/{endpoint}"
        params = params or {}
        params["appid"] = self.API_KEY
        params["units"] = "metric"
        headers = {"User-Agent": self.USER_AGENT}
        data = await async_get(url, params=params, headers=headers)
        if "error" in data:
            logger.error(
                f"Weather API failed | endpoint={endpoint} | error={data['error']}"
            )
            return None
        return data

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
        return f"Weather in {data['city']} | Condition: {data['condition']} | Temp: {data['temp']}C (Feels like {data['feels_like']}C) | Humidity: {data['humidity']}% | Wind: {data['wind']} km/h"

    def format_forecast(self, data: dict) -> str:
        lines = [f"Forecast for {data['city']}:"]
        for d in data["forecast"]:
            lines.append(f"  {d['day']}: {d['temp']}C, {d['condition']}")
        return "\n".join(lines)


if __name__ == "__main__":
    server = WeatherMCPServer()
    server.start()
