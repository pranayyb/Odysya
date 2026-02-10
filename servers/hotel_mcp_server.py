import asyncio
from typing import Any
from mcp.server.fastmcp import FastMCP
import random
from data.hotel_data import HOTEL_DATA, HOTEL_DESTINATIONS
from interfaces.mcp_server_interface import MCPServer
from utils.logger import get_logger
from utils.http_client import async_get
from config import HOTEL_MOCK_BOOL, BOOKING_API_BASE, RAPIDAPI_KEY

logger = get_logger("HotelMCPServer")


class HotelMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("hotel")
        self.BOOKING_API_BASE = BOOKING_API_BASE
        self.RAPIDAPI_KEY = RAPIDAPI_KEY
        self.USER_AGENT = "hotel-app/1.0"
        self.MOCK_LOCATIONS = HOTEL_DESTINATIONS
        self.MOCK_HOTELS = HOTEL_DATA
        self.USE_MOCK_DATA = HOTEL_MOCK_BOOL
        logger.info(f"HotelMCPServer initialized | mock_mode={self.USE_MOCK_DATA}")

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def search_hotels(
            location: str,
            min_price: float = 0,
            max_price: float = 1000,
            checkin_date: str = "2024-12-01",
            checkout_date: str = "2024-12-02",
        ) -> str:
            logger.info(
                f"search_hotels called | location={location} | price={min_price}-{max_price}"
            )
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            location_data = await self.search_location(location)
            if not location_data:
                logger.warning(f"Location not found: {location}")
                return f"Unable to find location: {location}.{mock_indicator}"
            dest_id = location_data.get("dest_id")
            dest_type = location_data.get("dest_type", "city")
            if not dest_id:
                return f"Unable to get destination ID for {location}.{mock_indicator}"
            url = f"{self.BOOKING_API_BASE}/hotels/search"
            params = {
                "dest_id": dest_id,
                "dest_type": dest_type,
                "checkin_date": checkin_date,
                "checkout_date": checkout_date,
                "adults_number": 2,
                "room_number": 1,
                "filter_by_currency": "USD",
                "order_by": "popularity",
                "units": "metric",
                "include_adjacency": "true",
            }
            data = await self.make_booking_request(url, params)
            if not data or "result" not in data:
                logger.warning(f"No hotel data returned for {location}")
                return f"Unable to fetch hotel data for this location.{mock_indicator}"
            hotels = data["result"]
            if not hotels:
                return f"No hotels found in {location}.{mock_indicator}"
            filtered_hotels = [
                h
                for h in hotels
                if h.get("min_total_price", 0)
                and min_price <= float(h["min_total_price"]) <= max_price
            ]
            if not filtered_hotels:
                return f"No hotels found in {location} within price range ${min_price}-${max_price}.{mock_indicator}"
            hotel_list = [self.format_hotel(hotel) for hotel in filtered_hotels[:10]]
            result = f"Hotels in {location} (${min_price}-${max_price} price range){mock_indicator}:\n"
            result += "\n---\n".join(hotel_list)
            result += f"\n\nShowing {len(hotel_list)} hotels out of {len(filtered_hotels)} matching results."
            logger.info(
                f"search_hotels returned {len(hotel_list)} hotels for {location}"
            )
            return result

        @self.mcp.tool()
        async def get_hotel_details(hotel_id: str) -> str:
            logger.info(f"get_hotel_details called | hotel_id={hotel_id}")
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.BOOKING_API_BASE}/hotels/details"
            params = {"hotel_id": hotel_id, "locale": "en-gb"}
            data = await self.make_booking_request(url, params)
            if not data:
                return f"Unable to fetch hotel details.{mock_indicator}"
            name = data.get("hotel_name", "Unknown Hotel")
            description = data.get("description", "No description available")
            facilities = data.get("facilities", [])
            address = data.get("address", "Address not available")
            rating = data.get("review_score", "N/A")
            details = f"Hotel: {name}{mock_indicator}\nRating: {rating}/10\nAddress: {address}\nDescription: {description}\nFacilities: {', '.join([f.get('name', '') for f in facilities]) if facilities else 'No facilities listed'}"
            logger.info(f"get_hotel_details returned details for {name}")
            return details

        @self.mcp.tool()
        async def search_hotels_by_coordinates(
            latitude: float,
            longitude: float,
            min_price: float = 0,
            max_price: float = 1000,
            checkin_date: str = "2025-12-01",
            checkout_date: str = "2025-12-02",
        ) -> str:
            logger.info(
                f"search_hotels_by_coordinates | lat={latitude}, lon={longitude}"
            )
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            url = f"{self.BOOKING_API_BASE}/hotels/search"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "checkin_date": checkin_date,
                "checkout_date": checkout_date,
                "adults_number": 2,
                "room_number": 1,
                "filter_by_currency": "USD",
                "order_by": "distance",
                "units": "metric",
            }
            data = await self.make_booking_request(url, params)
            if not data or "result" not in data:
                return f"Unable to fetch hotel data for this location.{mock_indicator}"
            hotels = data["result"]
            if not hotels:
                return (
                    f"No hotels found near ({latitude}, {longitude}).{mock_indicator}"
                )
            filtered_hotels = [
                h
                for h in hotels
                if h.get("min_total_price", 0)
                and min_price <= float(h["min_total_price"]) <= max_price
            ]
            if not filtered_hotels:
                return f"No hotels found near coordinates within ${min_price}-${max_price}.{mock_indicator}"
            hotel_list = [self.format_hotel(h) for h in filtered_hotels[:10]]
            result = f"Hotels near ({latitude}, {longitude}) (${min_price}-${max_price}){mock_indicator}:\n"
            result += "\n---\n".join(hotel_list)
            return result

    def start(self) -> None:
        logger.info("Starting Hotel MCP Server")
        asyncio.run(self.register_tools())
        self.mcp.run(transport="stdio")

    async def make_booking_request(
        self, url: str, params: dict = None
    ) -> dict[str, Any] | None:
        if self.USE_MOCK_DATA:
            return self.get_mock_response(url, params)
        headers = {
            "X-RapidAPI-Key": self.RAPIDAPI_KEY,
            "X-RapidAPI-Host": "booking-com.p.rapidapi.com",
            "User-Agent": self.USER_AGENT,
        }
        data = await async_get(url, params=params, headers=headers)
        if "error" in data:
            logger.error(
                f"Booking API request failed | url={url} | error={data['error']}"
            )
            return None
        return data

    def get_mock_response(self, url: str, params: dict = None) -> dict[str, Any] | None:
        if "/stays/search" in url:
            location_name = params.get("name", "").lower() if params else ""
            if location_name in self.MOCK_LOCATIONS:
                return [self.MOCK_LOCATIONS[location_name]]
            return [
                {"dest_id": "99999", "dest_type": "city", "name": location_name.title()}
            ]
        elif "/hotels/search" in url:
            hotels = self.MOCK_HOTELS.copy()
            for hotel in hotels:
                hotel["min_total_price"] = round(
                    hotel["min_total_price"] * random.uniform(0.8, 1.3), 2
                )
            return {"result": hotels}
        elif "/hotels/details" in url:
            hotel_id = params.get("hotel_id") if params else None
            for hotel in self.MOCK_HOTELS:
                if hotel["hotel_id"] == hotel_id:
                    return hotel
            return {
                "hotel_id": hotel_id,
                "hotel_name": "Mock Hotel",
                "description": "Mock hotel for testing.",
                "facilities": [{"name": "WiFi"}, {"name": "Parking"}],
                "address": "123 Mock St",
                "review_score": 7.5,
            }
        return None

    def format_hotel(self, hotel: dict) -> str:
        return f"Hotel: {hotel.get('hotel_name', 'Unknown')} | Price: {hotel.get('min_total_price', 'N/A')} {hotel.get('currency_code', 'USD')} | Rating: {hotel.get('review_score', 'N/A')}/10 | Address: {hotel.get('address', 'N/A')} | Distance: {hotel.get('distance_to_cc', 'N/A')} | ID: {hotel.get('hotel_id', 'N/A')}"

    async def search_location(self, location: str) -> dict | None:
        url = f"{self.BOOKING_API_BASE}/stays/search"
        params = {"name": location, "locale": "en-gb"}
        data = await self.make_booking_request(url, params)
        if data and len(data) > 0:
            return data[0]
        return None


if __name__ == "__main__":
    server = HotelMCPServer()
    server.start()
