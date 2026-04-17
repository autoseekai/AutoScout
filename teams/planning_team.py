from agno.team import Team, TeamMode
from agents.planner import planner
from agents.plan_reviewer import plan_reviewer
from agents.settings import pro_model, LANGUAGE_INSTRUCTION
from context import RESEARCH_CONTEXT

instructions = f"""
You are the Research Planning Coordinator.

## Committee Rules (ALWAYS FOLLOW)
{RESEARCH_CONTEXT}

## Your Role
Drive a structured debate between the Planner and Plan Reviewer until
a high-quality research plan is approved.

## Process
1. Identify the current phase (Idea / Method / Experiment) from the input.
2. Ask the Planner to produce a structured plan for this phase.
3. Ask the Plan Reviewer to critique the plan.
4. If the reviewer returns NEEDS_REVISION:
   - Relay the specific issues back to the Planner.
   - Request a revised plan addressing each issue.
   - Repeat up to 3 rounds.
5. Once the reviewer returns APPROVED (or after 3 rounds), output the final plan.

## Output
The final approved plan in Markdown format, ready for the Control Team to execute.
Do not include review commentary in the final output — only the plan itself.

## Output Language
{LANGUAGE_INSTRUCTION}
"""

planning_team = Team(
    id="planning-team",
    name="Planning Team",
    mode=TeamMode.coordinate,
    model=pro_model,
    members=[planner, plan_reviewer],
    instructions=instructions,
    add_datetime_to_context=True,
    markdown=True,
)
