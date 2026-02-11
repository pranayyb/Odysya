from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from models.itinerary import Itinerary


ITINERARY_SYSTEM_PROMPT = """You are an expert travel itinerary planner. Create comprehensive, 
practical day-by-day itineraries that optimize time, budget, and user preferences. 
Include specific timings, transportation between locations, meal recommendations, 
and practical tips. Format your response as a detailed, structured itinerary.

CRITICAL RULES:
- ONLY use hotels, restaurants, transport options, events, tourist places, and weather data that are explicitly 
  provided in the AVAILABLE OPTIONS section below. Do NOT invent or hallucinate any venue names, 
  restaurants, hotels, places, prices, or events that are not listed.
- If a category says "No specific options available", acknowledge it and suggest the traveler 
  research options upon arrival, but do NOT fabricate specific names or details.
- Reference the provided options BY NAME and include their actual prices, ratings, and details.
- Be specific with times, addresses, and costs FROM THE PROVIDED DATA.
- Factor in realistic travel times between locations
- Include weather-appropriate activities based on the PROVIDED weather forecast
- Stay within the stated budget
- Prioritize the user's stated preferences
- Include backup plans for weather issues
- Add practical local tips and insights
"""


def _format_item(item: Any) -> str:
    if isinstance(item, dict):
        parts = []
        for key, value in item.items():
            if value is not None and value != [] and value != "":
                if isinstance(value, list):
                    parts.append(f"  {key}: {', '.join(str(v) for v in value)}")
                else:
                    parts.append(f"  {key}: {value}")
        return "\n".join(parts)
    return str(item)


def _format_data_section(data: Any) -> str:
    if not data or data == ["No results available"]:
        return "No specific options available"

    if isinstance(data, str):
        return data

    if isinstance(data, dict):
        list_key = None
        for key, value in data.items():
            if isinstance(value, list) and key not in ("success"):
                list_key = key
                break

        if list_key and data[list_key]:
            items = data[list_key]
            formatted = []
            for i, item in enumerate(items, 1):
                formatted.append(f"Option {i}:")
                formatted.append(_format_item(item))
            notes = data.get("notes")
            if notes:
                formatted.append(f"\nNotes: {notes}")
            return "\n".join(formatted)

        notes = data.get("notes")
        if notes:
            return f"Notes: {notes}"
        formatted = []
        for key, value in data.items():
            if key != "success" and value is not None:
                formatted.append(f"- {key}: {value}")
        return "\n".join(formatted) if formatted else "No specific options available"

    if isinstance(data, list):
        if not data:
            return "No specific options available"
        formatted = []
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                formatted.append(f"Option {i}:")
                formatted.append(_format_item(item))
            else:
                formatted.append(f"- {item}")
        return "\n".join(formatted)

    return str(data)[:500] + "..." if len(str(data)) > 500 else str(data)


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

PLACES & ATTRACTIONS:
{_format_data_section(data.attractions)}

WEATHER:
{_format_data_section(data.weather)}

REQUIREMENTS:
1. Create a day-by-day schedule with specific times
2. Include travel time between locations
3. Suggest meal times and restaurants FROM THE OPTIONS LISTED ABOVE ONLY
4. Factor in the weather conditions PROVIDED ABOVE
5. Stay within budget constraints
6. Prioritize user preferences
7. Include backup plans for weather issues
8. Add practical tips and local insights
9. Suggest optimal routes and timing
10. Include rest periods and buffer time
11. ONLY reference hotels, restaurants, events, tourist places, and transport that appear in AVAILABLE OPTIONS above
12. If data is missing for a category, say so — do NOT make up names or details

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
