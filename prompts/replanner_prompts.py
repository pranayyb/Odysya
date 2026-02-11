import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.planner_state import PlannerState


REPLANNER_SYSTEM_PROMPT = """You are a ReAct trip planning agent. Follow this process:
1. THINK: Analyze the trip planning results against user requirements (budget, preferences, destination, dates)
2. ACT: Identify specific issues and determine what needs improvement
3. DECIDE: Make concrete decisions about which agents to rerun and what adjustments to make

Be specific and actionable in your decisions. Use exact agent names: 'hotel', 'transport', 'restaurant', 'weather', 'event', 'attraction'.

Rules:
- If an agent failed, always add it to retries.
- If results don't match user budget or preferences, flag the issue and retry the relevant agent.
- If all results look reasonable and complete, set done=true and retries=[].
- Never retry more than what is needed. Be efficient.
- Provide clear notes summarizing your reasoning.
"""


def build_replan_prompt(state: "PlannerState") -> str:
    trip = state["trip"]
    prompt = f"""
THINK → ACT → DECIDE: Analyze this trip planning scenario using ReAct methodology.

USER TRIP REQUEST:
- Destination: {trip.destination}
- Start Date: {trip.start_date}
- End Date: {trip.end_date}
- Budget: ${trip.budget if trip.budget else 'No budget specified'}
- Preferences: {', '.join(trip.preferences) if trip.preferences else 'No specific preferences'}

AGENT RESULTS STATUS:
"""

    for agent_name, result_key in [
        ("Hotel", "hotel_result"),
        ("Transport", "transport_result"),
        ("Restaurant", "restaurant_result"),
        ("Weather", "weather_result"),
        ("Event", "event_result"),
        ("Attraction", "attraction_result"),
    ]:
        result = state.get(result_key)
        if result:
            prompt += f"\n{agent_name}: {'Success' if result.success else 'Failed'}\n"
            if result.success and result.data:
                data_str = json.dumps(result.data, indent=2, default=str)
                prompt += f"  Data: {data_str[:300]}...\n"
            if result.error:
                prompt += f"  Error: {result.error}\n"
        else:
            prompt += f"\n{agent_name}: ⏳ No results available\n"

    prompt += f"""
PREVIOUS RETRIES: {state.get('retries', [])}
RETRY COUNT SO FAR: {state.get('retry_count', 0)}
MAX RETRIES ALLOWED: 3

THINK: What issues do you see with the current results?
ACT: Which specific problems need to be addressed?
DECIDE:
1. Which agents need to be rerun? (use exact names: 'hotel', 'transport', 'restaurant', 'weather', 'event', 'attraction')
2. What adjustments to trip parameters are needed?
3. What specific issues were identified?
4. Is the planning complete (done=true) or should we continue (done=false)?

Be concrete and actionable in your decisions.
If max retries have been reached, set done=true and provide best-effort notes.
"""
    return prompt
