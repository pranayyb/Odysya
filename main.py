import asyncio
from models.trip_request import TripRequest
from utils.validator import validate_trip_request
from agents.planner_agent import travel_planner

if __name__ == "__main__":
    trip_request = {
        "destination": "Mumbai",
        "start_date": "2025-06-01",
        "end_date": "2025-06-05",
        "preferences": ["food"],
        "budget": 2000.0,
    }
    trip_request: TripRequest = validate_trip_request(trip_request)
    initial_state = {
        "trip": trip_request,
        "retries": [],
        "done": False,
        "notes": "",
        "hotel_result": None,
        "transport_result": None,
        "restaurant_result": None,
        "weather_result": None,
        "event_result": None,
        "aggregated_plan": None,
        "final_itinerary": None,
    }
    result = asyncio.run(travel_planner.ainvoke(initial_state, {"recursion_limit": 50}))
    print("\nTRIP PLANNING COMPLETED!")
    print(
        "\nDetailed Itinerary:",
        result.get("final_itinerary", {}).get(
            "detailed_itinerary", "No detailed itinerary generated"
        ),
    )
