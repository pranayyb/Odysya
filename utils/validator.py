from models.trip_request import TripRequest


def validate_trip_request(data: dict) -> TripRequest:
    try:
        return TripRequest(**data)
    except Exception as e:
        raise ValueError(f"Invalid TripRequest: {e}")
