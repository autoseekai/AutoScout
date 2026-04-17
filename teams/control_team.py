from agno.team import Team, TeamMode
from agents.idea_maker import idea_maker
from agents.idea_hater import idea_hater
from agents.researcher import researcher
from agents.engineer import engineer
from agents.docker_executor import docker_executor
from agents.settings import pro_model, LANGUAGE_INSTRUCTION
from context import RESEARCH_CONTEXT

instructions = f"""
You are the Research Execution Coordinator.

## Committee Rules (ALWAYS FOLLOW)
{RESEARCH_CONTEXT}

## Your Role
Read the task plan and select the appropriate combination of specialists to
complete it.

- **Idea Maker**: Generate hypotheses, research directions.
- **Idea Hater**: Pressure-test hypotheses from the Idea Maker.
- **Researcher**: Gather evidence and literature.
- **Engineer**: Writes the pure code/scripts required for experiments.
- **Docker Executor**: Runs the Engineer's code in isolated Docker containers to capture stdout/stderr.

## Execution Rules
1. Invoke members sequentially or in pairs as logic dictates.
2. For experimental tasks, always pair the Engineer (to write code) with the Docker Executor (to execute and test it).
3. Synthesise their outputs into a single, cohesive Phase deliverable.

## Output
A single Markdown document synthesising findings from all invocations.
"""

control_team = Team(
    id="control-team",
    name="Control Team",
    mode=TeamMode.coordinate,
    model=pro_model,
    members=[idea_maker, idea_hater, researcher, engineer, docker_executor],
    instructions=instructions,
    add_datetime_to_context=True,
    markdown=True,
)
