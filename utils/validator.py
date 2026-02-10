from models.trip_request import TripRequest
from utils.logger import get_logger

logger = get_logger("Validator")


def validate_trip_request(data: dict) -> TripRequest:
    try:
        trip = TripRequest(**data)
        logger.info(
            f"Validated trip request: destination={trip.destination}, "
            f"dates={trip.start_date} to {trip.end_date}, budget={trip.budget}"
        )
        return trip
    except Exception as e:
        logger.error(f"Invalid TripRequest: {e}")
        raise ValueError(f"Invalid TripRequest: {e}")
