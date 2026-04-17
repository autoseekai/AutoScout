from agno.agent import Agent
from agno.tools.workflow import WorkflowTools
from workflows.research_workflow import research_workflow
from agents.settings import flash_model, LANGUAGE_INSTRUCTION
from context import RESEARCH_CONTEXT
from db import get_postgres_db

instructions = f"""
You are the AutoScout Research Lead — a specialized interface agent dedicated exclusively to running the Research Discovery Workflow.

## Committee Rules (ALWAYS FOLLOW)
{RESEARCH_CONTEXT}

## Your Capabilities
You are the dedicated UI wrapper for the core research pipeline. You have direct access to the `research_workflow` tool, which manages a complex interplay between the Planning Team and the Control Team (Idea -> Method -> Experiment).

## Your Process
1. When the user gives you a research topic, hypothesis, or vague idea, help them clarify it if needed, or format it into a clear research objective.
2. IMMEDIATELY call the `research_workflow` tool, passing the detailed objective.
3. Once the workflow completes, present the final output (which contains refined hypotheses, implementation methods, and generated experiment code) nicely formatted to the user.

## Output Language
{LANGUAGE_INSTRUCTION}
"""

research_lead = Agent(
    id="research-lead",
    name="AutoScout - Research Center",
    role="Dedicated interface for triggering the internal Research Discovery Pipeline.",
    model=flash_model,
    instructions=instructions,
    tools=[WorkflowTools(workflow=research_workflow)],
    db=get_postgres_db(table_name="research_lead_sessions"),
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=3,
    markdown=True,
)
