from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from models.itinerary import Itinerary


ITINERARY_SYSTEM_PROMPT = """You are an expert travel itinerary planner. Create comprehensive, 
practical day-by-day itineraries that optimize time, budget, and user preferences. 
Include specific timings, transportation between locations, meal recommendations, 
and practical tips. Format your response as a detailed, structured itinerary.

Guidelines:
- Be specific with times, addresses, and costs
- Factor in realistic travel times between locations
- Include weather-appropriate activities
- Stay within the stated budget
- Prioritize the user's stated preferences
- Include backup plans for weather issues
- Add practical local tips and insights
"""


def _format_data_section(data: Any) -> str:
    if not data or data == ["No results available"]:
        return "No specific options available"

    if isinstance(data, str):
        return data

    if isinstance(data, list):
        return "\n".join([f"- {item}" for item in data[:5]])

    if isinstance(data, dict):
        formatted = []
        for key, value in list(data.items())[:3]:
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)

    return str(data)[:200] + "..." if len(str(data)) > 200 else str(data)


def build_itinerary_prompt(data: "Itinerary") -> str:
    trip = data.trip

    prompt = f"""
Create a detailed day-by-day itinerary for this trip:

TRIP DETAILS:
Destination: {trip.destination}
Dates: {trip.start_date} to {trip.end_date}
Budget: ${trip.budget if trip.budget else 'Flexible'}
Preferences: {', '.join(trip.preferences) if trip.preferences else 'General tourism'}

AVAILABLE OPTIONS:

HOTELS:
{_format_data_section(data.hotels)}

TRANSPORT:
{_format_data_section(data.transport)}

RESTAURANTS:
{_format_data_section(data.restaurants)}

EVENTS & ACTIVITIES:
{_format_data_section(data.events)}

WEATHER:
{_format_data_section(data.weather)}

REQUIREMENTS:
1. Create a day-by-day schedule with specific times
2. Include travel time between locations
3. Suggest meal times and restaurants
4. Factor in weather conditions
5. Stay within budget constraints
6. Prioritize user preferences
7. Include backup plans for weather issues
8. Add practical tips and local insights
9. Suggest optimal routes and timing
10. Include rest periods and buffer time

Format as:
DAY 1 (Date): Theme/Focus

Morning (9:00 AM – 12:00 PM):
9:00 AM – 9:15 AM: Activity description with specific details.
9:15 AM – 9:45 AM: Next activity with transit info.
...

Afternoon (12:00 PM – 5:00 PM):
...

Evening (5:00 PM – 10:00 PM):
...

Continue for each day...
"""
    return prompt
