from typing import Any, Dict
from config import llm_model
from models import Itinerary
from langchain_core.messages import HumanMessage, SystemMessage


class ItineraryAgent:
    def __init__(self):
        self.llm = llm_model

    async def generate_detailed_itinerary(
        self, aggregated_data: Itinerary
    ) -> Dict[str, Any]:
        try:
            prompt = self._build_itinerary_prompt(aggregated_data)
            messages = [
                SystemMessage(
                    content="""You are an expert travel itinerary planner. Create comprehensive, 
                practical day-by-day itineraries that optimize time, budget, and user preferences. 
                Include specific timings, transportation between locations, meal recommendations, 
                and practical tips. Format your response as a detailed, structured itinerary."""
                ),
                HumanMessage(content=prompt),
            ]
            response = await self.llm.ainvoke(messages)

            return {
                "detailed_itinerary": response.content,
                "key_recommendations": self._extract_key_recommendations(
                    aggregated_data
                ),
            }

        except Exception as e:
            return {
                "detailed_itinerary": f"Error generating itinerary: {str(e)}",
                "summary": "Unable to generate summary due to error",
                "total_estimated_cost": 0,
                "key_recommendations": [],
            }

    def _build_itinerary_prompt(self, data: Itinerary) -> str:
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
        {self._format_data_section(data.hotels)}
        
        TRANSPORT:
        {self._format_data_section(data.transport)}
        
        RESTAURANTS:
        {self._format_data_section(data.restaurants)}

        EVENTS & ACTIVITIES:
        {self._format_data_section(data.events)}

        WEATHER:
        {self._format_data_section(data.weather)}
        
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
        DAY 1 (November 10, 2025): Traditional Tokyo & Cultural Exploration

        Morning (9:00 AM – 12:00 PM):
        9:00 AM – 9:15 AM: Depart hotel (Shinjuku area) via Toei Oedo Line to Asakusa (~25 min including transfer).
        9:15 AM – 9:45 AM: Breakfast at Tsumugi Asakusa — traditional Japanese breakfast set (~¥1500).
        9:45 AM – 11:00 AM: Visit Senso-ji Temple; explore temple grounds, Nakamise shopping street for souvenirs/snacks.
        11:00 AM – 11:45 AM: Walk to Sumida River area (10 min) and enjoy short riverside stroll or rest at Sumida Park.
        11:45 AM – 12:00 PM: Depart for Ueno via Tokyo Metro Ginza Line (15 min).

        Continue for each day...
        """
        return prompt

    def _format_data_section(self, data: Any) -> str:
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

    def _extract_key_recommendations(self, data: Itinerary) -> list:
        recommendations = []
        if data.weather and data.weather != ["No results available"]:
            recommendations.append("Check weather updates before outdoor activities")
        if data.trip.budget:
            recommendations.append(f"Stay within ${data.trip.budget} budget")
        if data.trip.preferences:
            recommendations.append(
                f"Focus on {', '.join(data.trip.preferences)} activities"
            )
        recommendations.append("Book accommodations and transport in advance")
        recommendations.append("Keep backup plans for weather-dependent activities")
        return recommendations
