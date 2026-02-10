from config import llm_model
from models.planner_state import PlannerState
from models.replanner import ReplanDecision
from utils.logger import get_logger
from prompts.replanner_prompts import REPLANNER_SYSTEM_PROMPT, build_replan_prompt

logger = get_logger("ReplanAgent")


class ReplanAgent:
    def __init__(self):
        self.llm = llm_model
        self.decision_agent = llm_model.with_structured_output(ReplanDecision)
        logger.info("ReplanAgent initialized")

    def analyze_planner_state(self, state: PlannerState) -> ReplanDecision:
        logger.info("ReplanAgent.analyze_planner_state called")
        decision_prompt = build_replan_prompt(state)
        decision = self.decision_agent.invoke(
            [
                {"role": "system", "content": REPLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": decision_prompt},
            ]
        )
        logger.info(
            f"ReplanAgent decision | done={decision.done} | retries={decision.retries} "
            f"| notes={decision.notes[:100]}..."
        )
        return decision
