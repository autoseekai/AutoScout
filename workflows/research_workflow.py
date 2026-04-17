from typing import List
from agno.workflow import Loop, Steps, Step, Workflow
from agno.workflow.types import StepOutput
from agents.execution_manager import ManagerDecision
from teams.planning_team import planning_team
from teams.control_team import control_team
from agents.execution_manager import execution_manager
from db.session import get_postgres_db


# ---------------------------------------------------------------------------
# Loop termination condition
# ---------------------------------------------------------------------------

def check_satisfied(outputs: List[StepOutput]) -> bool:
    """Return True to break the loop when the Execution Manager signals DONE.

    Parses the last step output (Manager Evaluation) as ManagerDecision JSON.
    Falls back to string matching if JSON parsing fails.
    """
    if not outputs:
        return False

    last = outputs[-1]
    content = last.content or ""

    # Primary: parse structured output
    try:
        decision = ManagerDecision.model_validate_json(content)
        return decision.signal == "DONE"
    except Exception:
        pass

    # Fallback: string matching
    return "DONE" in content or '"signal": "DONE"' in content


# ---------------------------------------------------------------------------
# Phase step groups (reuse planning_team and control_team across all phases)
# ---------------------------------------------------------------------------

idea_phase = Steps(
    name="Idea Phase",
    steps=[
        Step(name="Idea — Plan",    agent=planning_team),
        Step(name="Idea — Execute", agent=control_team),
    ],
)

method_phase = Steps(
    name="Method Phase",
    steps=[
        Step(name="Method — Plan",    agent=planning_team),
        Step(name="Method — Execute", agent=control_team),
    ],
)

experiment_phase = Steps(
    name="Experiment Phase",
    steps=[
        Step(name="Experiment — Plan",    agent=planning_team),
        Step(name="Experiment — Execute", agent=control_team),
    ],
)

# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------

research_workflow = Workflow(
    id="research-workflow",
    name="Research Discovery Pipeline",
    description=(
        "Iterative research pipeline: Idea → Method → Experiment, "
        "driven by an Execution Manager that refines the goal each iteration."
    ),
    db=get_postgres_db(table_name="research_workflow_sessions"),
    steps=[
        Loop(
            name="Research Iteration Loop",
            steps=[
                idea_phase,
                method_phase,
                experiment_phase,
                Step(
                    name="Manager Evaluation",
                    agent=execution_manager,
                    add_workflow_history=True,
                    num_history_runs=3,
                ),
            ],
            end_condition=check_satisfied,
            max_iterations=1,
            forward_iteration_output=True,
        ),
    ],
)


# ---------------------------------------------------------------------------
# Entry point (for direct execution / testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    research_workflow.print_response(
        "Research the technical feasibility of using local LLMs for real-time "
        "financial signal generation in a low-latency trading environment.",
        markdown=True,
    )
