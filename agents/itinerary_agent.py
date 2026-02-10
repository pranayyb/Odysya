from typing import Any, Dict
from config import llm_model
from models import Itinerary
from langchain_core.messages import HumanMessage, SystemMessage
from utils.logger import get_logger
from prompts.itinerary_prompts import ITINERARY_SYSTEM_PROMPT, build_itinerary_prompt

logger = get_logger("ItineraryAgent")


class ItineraryAgent:
    def __init__(self):
        self.llm = llm_model
        logger.info("ItineraryAgent initialized")

    async def generate_detailed_itinerary(
        self, aggregated_data: Itinerary
    ) -> Dict[str, Any]:
        logger.info("ItineraryAgent.generate_detailed_itinerary called")
        try:
            prompt = build_itinerary_prompt(aggregated_data)
            messages = [
                SystemMessage(content=ITINERARY_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
            response = await self.llm.ainvoke(messages)
            logger.info(
                f"ItineraryAgent generated itinerary | length={len(response.content)}"
            )

            return {
                "detailed_itinerary": response.content,
                "key_recommendations": self._extract_key_recommendations(
                    aggregated_data
                ),
            }

        except Exception as e:
            logger.error(
                f"ItineraryAgent.generate_detailed_itinerary failed | error={e}"
            )
            return {
                "detailed_itinerary": f"Error generating itinerary: {str(e)}",
                "summary": "Unable to generate summary due to error",
                "total_estimated_cost": 0,
                "key_recommendations": [],
            }

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
        logger.info(f"Generated {len(recommendations)} key recommendations")
        return recommendations
