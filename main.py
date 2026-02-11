from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from models.trip_request import TripRequest
from models.planner_state import PlannerState
from utils.validator import validate_trip_request
from utils.logger import get_logger
from agents.planner_agent import travel_planner

logger = get_logger("Main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Odysya starting up")
    yield
    logger.info("Odysya shutting down")


app = FastAPI(
    title="Odysya",
    description="AI-powered travel planning API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    logger.info("GET /health")
    return {"status": "ok"}


@app.post("/plan")
async def plan_trip(request: TripRequest):
    logger.info(f"POST /plan | destination={request.destination}")

    try:
        trip: TripRequest = validate_trip_request(request.model_dump())
    except ValueError as e:
        logger.error(f"Validation failed | error={e}")
        raise HTTPException(status_code=422, detail=str(e))

    initial_state = PlannerState.create(trip)

    try:
        logger.info("Invoking travel planner graph...")
        result = await travel_planner.ainvoke(initial_state, {"recursion_limit": 50})
    except Exception as e:
        logger.error(f"Planner failed | error={e}")
        raise HTTPException(status_code=500, detail=f"Planning failed: {e}")

    final_itinerary = result.get("final_itinerary", {})
    detailed = None
    recommendations = []

    if isinstance(final_itinerary, dict):
        detailed = final_itinerary.get("detailed_itinerary")
        recommendations = final_itinerary.get("key_recommendations", [])
    elif final_itinerary:
        detailed = str(final_itinerary)

    logger.info(
        f"Plan complete | destination={request.destination} | retries={result.get('retry_count', 0)}"
    )

    return {
        "success": True,
        "destination": request.destination,
        "detailed_itinerary": detailed,
        "key_recommendations": recommendations,
        "retry_count": result.get("retry_count", 0),
        "notes": result.get("notes", ""),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
