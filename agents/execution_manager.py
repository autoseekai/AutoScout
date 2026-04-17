from typing import Literal
from pydantic import BaseModel
from agno.agent import Agent
from agents.settings import pro_model, LANGUAGE_INSTRUCTION
from context import RESEARCH_CONTEXT
from db.session import get_postgres_db


class ManagerDecision(BaseModel):
    signal: Literal["DONE", "CONTINUE"]
    refined_goal: str = ""   # Only populated when signal == "CONTINUE"
    reason: str              # Always required — explains the decision


instructions = f"""
You are the Research Iteration Manager — the final evaluator after each full
Idea → Method → Experiment cycle.

## Committee Rules (ALWAYS FOLLOW)
{RESEARCH_CONTEXT}

## Your Role
Given the current research goal and the Experiment phase results, decide whether
the research objectives have been sufficiently addressed.

## Decision Criteria
- signal="DONE" when:
  - The experiment results contain concrete, actionable findings.
  - The original research goal is directly answered.
  - Further iteration would yield diminishing returns.

- signal="CONTINUE" when:
  - Key questions remain unanswered.
  - Findings are too shallow or too broad.
  - A more focused angle would significantly improve outcomes.
  In this case, refined_goal must be a more specific, actionable version
  of the original goal that targets the identified gap.

## Output
Return a JSON object matching the ManagerDecision schema.
Always include a clear reason for your decision.
signal, refined_goal, reason are all required.

## Output Language
{LANGUAGE_INSTRUCTION}
"""

execution_manager = Agent(
    id="execution-manager",
    name="Execution Manager",
    model=pro_model,
    instructions=instructions,
    db=get_postgres_db(table_name="research_lead_sessions"),
    output_schema=ManagerDecision,
    add_datetime_to_context=True,
    markdown=False,   # Structured JSON output — no markdown wrapping
)
