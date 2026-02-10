import asyncio
from models.trip_request import TripRequest
from utils.validator import validate_trip_request
from utils.logger import get_logger
from agents.planner_agent import travel_planner

logger = get_logger("TestWorkflow")


async def run_planner():
    trip_request = {
        "destination": "Mumbai",
        "start_date": "2025-06-01",
        "end_date": "2025-06-05",
        "preferences": ["food"],
        "budget": 2000.0,
    }

    logger.info(f"Starting trip planning | destination={trip_request['destination']}")
    trip: TripRequest = validate_trip_request(trip_request)

    initial_state = {
        "trip": trip,
        "retries": [],
        "retry_count": 0,
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

    logger.info("Invoking travel planner graph...")
    result = await travel_planner.ainvoke(initial_state, {"recursion_limit": 50})

    logger.info("Trip planning completed")

    print("\n" + "=" * 60)
    print("  TRIP PLANNING COMPLETED!")
    print("=" * 60)

    final_itinerary = result.get("final_itinerary", {})
    if isinstance(final_itinerary, dict):
        detailed = final_itinerary.get("detailed_itinerary", "No detailed itinerary generated")
        recommendations = final_itinerary.get("key_recommendations", [])

        print("\n📋 DETAILED ITINERARY:")
        print("-" * 40)
        print(detailed)

        if recommendations:
            print("\n💡 KEY RECOMMENDATIONS:")
            print("-" * 40)
            for rec in recommendations:
                print(f"  • {rec}")
    else:
        print("\n📋 ITINERARY:")
        print(final_itinerary)

    print("\n" + "=" * 60)

    # Log summary
    retry_count = result.get("retry_count", 0)
    notes = result.get("notes", "")
    logger.info(f"Final state | retry_count={retry_count} | notes={notes[:100]}...")


if __name__ == "__main__":
    asyncio.run(run_planner())
