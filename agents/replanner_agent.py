from config import llm_model
from models.planner_state import PlannerState
from models.replanner import ReplanDecision
from models.trip_request import TripRequest
from models.agent_response import AgentResponse
import json


class ReplanAgent:
    def __init__(self):
        self.llm = llm_model
        self.decision_agent = llm_model.with_structured_output(ReplanDecision)

    def analyze_planner_state(self, state: PlannerState) -> ReplanDecision:
        decision_prompt = self._build_replan_prompt(state)
        decision = self.decision_agent.invoke(
            [
                {
                    "role": "system",
                    "content": """You are a ReAct trip planning agent. Follow this process:
                        1. THINK: Analyze the trip planning results against user requirements (budget, preferences, destination, dates)
                        2. ACT: Identify specific issues and determine what needs improvement  
                        3. DECIDE: Make concrete decisions about which agents to rerun and what adjustments to make
                        Be specific and actionable in your decisions. Use exact agent names: 'hotel', 'transport', 'restaurant', 'weather', 'event'.""",
                },
                {"role": "user", "content": decision_prompt},
            ]
        )
        return decision

    def _build_replan_prompt(self, state: PlannerState) -> str:
        prompt = f"""
        THINK → ACT → DECIDE: Analyze this trip planning scenario using ReAct methodology.
        USER TRIP REQUEST:
        - Destination: {state['trip'].destination}
        - Start Date: {state['trip'].start_date}
        - End Date: {state['trip'].end_date}
        - Budget: ${state['trip'].budget if state['trip'].budget else 'No budget specified'}
        - Preferences: {', '.join(state['trip'].preferences) if state['trip'].preferences else 'No specific preferences'}
        AGENT RESULTS STATUS:
        """

        for agent_name, result_key in [
            ("Hotel", "hotel_result"),
            ("Transport", "transport_result"),
            ("Restaurant", "restaurant_result"),
            ("Weather", "weather_result"),
            ("Event", "event_result"),
        ]:
            result = state.get(result_key)
            if result:
                prompt += (
                    f"\n{agent_name}: {'Success' if result.success else 'Failed'}\n"
                )
                if result.success and result.data:
                    prompt += f"  Data: {json.dumps(result.data, indent=2)[:200]}...\n"
                if result.error:
                    prompt += f"  Error: {result.error}\n"
            else:
                prompt += f"\n{agent_name}: No results available\n"

        prompt += f"""
        PREVIOUS RETRIES: {state['retries']}
        THINK: What issues do you see with the current results?
        ACT: Which specific problems need to be addressed?
        DECIDE: 
        1. Which agents need to be rerun? (use exact names: 'hotel', 'transport', 'restaurant', 'weather', 'event')
        2. What adjustments to trip parameters are needed?
        3. What specific issues were identified?
        4. Is the planning complete (done=true) or should we continue (done=false)?
        Be concrete and actionable in your decisions.
        """
        return prompt


replan_agent = ReplanAgent()


## testing replanning
mock_state = PlannerState(
    trip=TripRequest(
        destination="Paris",
        start_date="2025-10-10",
        end_date="2025-10-20",
        budget=3000,
        preferences=["museum", "fine dining", "walking tours"],
    ),
    hotel_result=AgentResponse(
        agent_name="hotel", success=True, data={"name": "Hotel Parisian"}, error=None
    ),
    transport_result=AgentResponse(
        agent_name="transport",
        success=False,
        data=None,
        error="No available flights found",
    ),
    restaurant_result=AgentResponse(
        agent_name="restaurant",
        success=True,
        data={"recommendations": ["Le Gourmet", "Bistro Chez Moi"]},
        error=None,
    ),
    weather_result=AgentResponse(
        agent_name="weather", success=True, data={"forecast": "Sunny"}, error=None
    ),
    event_result=AgentResponse(
        agent_name="event", success=False, data=None, error="Event API timeout"
    ),
    retries=[],
)

decision = replan_agent.analyze_planner_state(mock_state)

print("Replan Decision JSON:")
print(json.dumps(decision.model_dump(), indent=2))
