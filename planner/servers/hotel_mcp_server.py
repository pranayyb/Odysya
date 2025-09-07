import asyncio
from typing import Any, Dict
import httpx
from mcp.server.fastmcp import FastMCP
import logging
import random

from interfaces.mcp_server_interface import MCPServer


class HotelMCPServer(MCPServer):
    def __init__(self):
        self.mcp = FastMCP("hotel")
        self.BOOKING_API_BASE = "https://booking-com.p.rapidapi.com/v1"
        self.RAPIDAPI_KEY = "8f79364a7dmshf35dce4492b3da2p17f81fjsn70acc5d1eff8"
        self.USER_AGENT = "hotel-app/1.0"
        self.MOCK_LOCATIONS = {
            "new york": {
                "dest_id": "20088325",
                "dest_type": "city",
                "name": "New York City",
            },
            "paris": {"dest_id": "20015732", "dest_type": "city", "name": "Paris"},
            "london": {"dest_id": "20023181", "dest_type": "city", "name": "London"},
            "tokyo": {"dest_id": "20023181", "dest_type": "city", "name": "Tokyo"},
            "dubai": {"dest_id": "20021500", "dest_type": "city", "name": "Dubai"},
            "mumbai": {"dest_id": "20019765", "dest_type": "city", "name": "Mumbai"},
            "delhi": {"dest_id": "20019769", "dest_type": "city", "name": "Delhi"},
            "lucknow": {"dest_id": "20019770", "dest_type": "city", "name": "Lucknow"},
        }
        self.MOCK_HOTELS = [
            {
                "hotel_id": "12345",
                "hotel_name": "Grand Palace Hotel",
                "min_total_price": 150.00,
                "currency_code": "USD",
                "review_score": 8.7,
                "address": "123 Main Street, City Center",
                "distance_to_cc": "0.5 km",
                "description": "Luxurious hotel in the heart of the city with premium amenities.",
                "facilities": [
                    {"name": "WiFi"},
                    {"name": "Pool"},
                    {"name": "Gym"},
                    {"name": "Restaurant"},
                ],
            },
            {
                "hotel_id": "12346",
                "hotel_name": "Budget Inn Express",
                "min_total_price": 45.00,
                "currency_code": "USD",
                "review_score": 7.2,
                "address": "456 Budget Road, Suburbs",
                "distance_to_cc": "3.2 km",
                "description": "Comfortable and affordable accommodation for budget travelers.",
                "facilities": [{"name": "WiFi"}, {"name": "Parking"}],
            },
            {
                "hotel_id": "12347",
                "hotel_name": "Luxury Resort & Spa",
                "min_total_price": 350.00,
                "currency_code": "USD",
                "review_score": 9.4,
                "address": "789 Ocean View Avenue, Beachfront",
                "distance_to_cc": "5.1 km",
                "description": "Five-star resort with spa services and ocean views.",
                "facilities": [
                    {"name": "WiFi"},
                    {"name": "Pool"},
                    {"name": "Spa"},
                    {"name": "Beach Access"},
                    {"name": "Restaurant"},
                    {"name": "Bar"},
                ],
            },
            {
                "hotel_id": "12348",
                "hotel_name": "Business Hotel Central",
                "min_total_price": 120.00,
                "currency_code": "USD",
                "review_score": 8.1,
                "address": "321 Business District, Financial Center",
                "distance_to_cc": "1.0 km",
                "description": "Modern business hotel with conference facilities.",
                "facilities": [
                    {"name": "WiFi"},
                    {"name": "Business Center"},
                    {"name": "Meeting Rooms"},
                    {"name": "Restaurant"},
                ],
            },
            {
                "hotel_id": "12349",
                "hotel_name": "Boutique Art Hotel",
                "min_total_price": 200.00,
                "currency_code": "USD",
                "review_score": 8.9,
                "address": "654 Art District, Cultural Quarter",
                "distance_to_cc": "2.3 km",
                "description": "Stylish boutique hotel featuring local art and unique design.",
                "facilities": [
                    {"name": "WiFi"},
                    {"name": "Art Gallery"},
                    {"name": "Cafe"},
                    {"name": "Library"},
                ],
            },
            {
                "hotel_id": "12350",
                "hotel_name": "Family Resort",
                "min_total_price": 180.00,
                "currency_code": "USD",
                "review_score": 8.5,
                "address": "987 Family Lane, Entertainment District",
                "distance_to_cc": "4.0 km",
                "description": "Family-friendly resort with kids' activities and entertainment.",
                "facilities": [
                    {"name": "WiFi"},
                    {"name": "Kids Club"},
                    {"name": "Pool"},
                    {"name": "Playground"},
                    {"name": "Restaurant"},
                ],
            },
            {
                "hotel_id": "12351",
                "hotel_name": "Eco Lodge",
                "min_total_price": 90.00,
                "currency_code": "USD",
                "review_score": 7.8,
                "address": "111 Green Valley, Nature Reserve",
                "distance_to_cc": "8.5 km",
                "description": "Sustainable eco-lodge surrounded by nature.",
                "facilities": [
                    {"name": "WiFi"},
                    {"name": "Hiking Trails"},
                    {"name": "Organic Restaurant"},
                    {"name": "Garden"},
                ],
            },
            {
                "hotel_id": "12352",
                "hotel_name": "Historic Manor",
                "min_total_price": 250.00,
                "currency_code": "USD",
                "review_score": 9.1,
                "address": "222 Heritage Street, Old Town",
                "distance_to_cc": "1.5 km",
                "description": "Beautifully restored historic manor with period furnishings.",
                "facilities": [
                    {"name": "WiFi"},
                    {"name": "Historic Tours"},
                    {"name": "Fine Dining"},
                    {"name": "Library"},
                ],
            },
        ]
        self.USE_MOCK_DATA = True

    async def register_tools(self) -> None:
        @self.mcp.tool()
        async def search_hotels(
            location: str,
            min_price: float = 0,
            max_price: float = 1000,
            checkin_date: str = "2024-12-01",
            checkout_date: str = "2024-12-02",
        ) -> str:
            mock_indicator = " (MOCK DATA)" if self.USE_MOCK_DATA else ""
            location_data = await self.search_location(location)
            if not location_data:
                return f"Unable to find location: {location}. Please try a different location name.{mock_indicator}"

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
                return f"Unable to fetch hotel data for this location.{mock_indicator}"

            hotels = data["result"]
            if not hotels:
                return f"No hotels found in {location}.{mock_indicator}"

            filtered_hotels = []
            for hotel in hotels:
                price = hotel.get("min_total_price", 0)
                if price and min_price <= float(price) <= max_price:
                    filtered_hotels.append(hotel)

            if not filtered_hotels:
                return f"No hotels found in {location} within price range ${min_price}-${max_price}.{mock_indicator}"

            hotel_list = [self.format_hotel(hotel) for hotel in filtered_hotels[:10]]
            result = f"Hotels in {location} (${min_price}-${max_price} price range){mock_indicator}:\n"
            result += "\n---\n".join(hotel_list)
            result += f"\n\nShowing {len(hotel_list)} hotels out of {len(filtered_hotels)} matching results."

            return result

        @self.mcp.tool()
        async def get_hotel_details(hotel_id: str) -> str:
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
            details = f"""
                        Hotel: {name}{mock_indicator}
                        Rating: {rating}/10
                        Address: {address}
                        Description: {description}
                        Facilities: {', '.join([f.get('name', '') for f in facilities]) if facilities else 'No facilities listed'}
                        """
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
                return f"No hotels found near coordinates ({latitude}, {longitude}).{mock_indicator}"

            filtered_hotels = []
            for hotel in hotels:
                price = hotel.get("min_total_price", 0)
                if price and min_price <= float(price) <= max_price:
                    filtered_hotels.append(hotel)

            if not filtered_hotels:
                return f"No hotels found near coordinates within price range ${min_price}-${max_price}.{mock_indicator}"

            hotel_list = [self.format_hotel(hotel) for hotel in filtered_hotels[:10]]
            result = f"Hotels near ({latitude}, {longitude}) (${min_price}-${max_price} price range){mock_indicator}:\n"
            result += "\n---\n".join(hotel_list)
            result += f"\n\nShowing {len(hotel_list)} hotels out of {len(filtered_hotels)} matching results."
            return result

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
        return f"Hotel Server mode switched to: {mode}"

    def start(self) -> None:
        logging.info("Starting Hotel MCP Server")
        logging.info(f"Mock mode enabled: {self.USE_MOCK_DATA}")
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
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, headers=headers, params=params, timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logging.error(f"API request failed: {e}")
                return None

    def get_mock_response(self, url: str, params: dict = None) -> dict[str, Any] | None:
        if "/stays/search" in url:
            location_name = params.get("name", "").lower() if params else ""
            if location_name in self.MOCK_LOCATIONS:
                return [self.MOCK_LOCATIONS[location_name]]
            else:
                return [
                    {
                        "dest_id": "99999",
                        "dest_type": "city",
                        "name": location_name.title(),
                    }
                ]

        elif "/hotels/search" in url:
            hotels = self.MOCK_HOTELS.copy()
            for hotel in hotels:
                base_price = hotel["min_total_price"]
                variation = random.uniform(0.8, 1.3)
                hotel["min_total_price"] = round(base_price * variation, 2)
            return {"result": hotels}

        elif "/hotels/details" in url:
            hotel_id = params.get("hotel_id") if params else None
            for hotel in self.MOCK_HOTELS:
                if hotel["hotel_id"] == hotel_id:
                    return hotel
            return {
                "hotel_id": hotel_id,
                "hotel_name": "Mock Hotel",
                "description": "This is a mock hotel for testing purposes.",
                "facilities": [{"name": "WiFi"}, {"name": "Parking"}],
                "address": "123 Mock Street, Test City",
                "review_score": 7.5,
            }

        return None

    def format_hotel(self, hotel: dict) -> str:
        name = hotel.get("hotel_name", "Unknown Hotel")
        price = hotel.get("min_total_price", "N/A")
        currency = hotel.get("currency_code", "USD")
        rating = hotel.get("review_score", "N/A")
        address = hotel.get("address", "Address not available")
        distance_to_cc = hotel.get("distance_to_cc", "N/A")

        return f"""
                Hotel: {name}
                Price: {price} {currency} (total)
                Rating: {rating}/10
                Address: {address}
                Distance to city center: {distance_to_cc}
                Hotel ID: {hotel.get("hotel_id", "N/A")}
                """

    async def search_location(self, location: str) -> dict | None:
        url = f"{self.BOOKING_API_BASE}/stays/search"
        params = {"name": location, "locale": "en-gb"}

        data = await self.make_booking_request(url, params)
        if data and len(data) > 0:
            return data[0]
        return None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    server = HotelMCPServer()
    server.start()
