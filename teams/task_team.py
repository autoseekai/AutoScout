from agno.team import Team, TeamMode
from agno.models.google import Gemini
from agents.interest_profiler import interest_profiler

task_team = Team(
    id="task-team",
    name="AutoScout - Tasks",
    mode=TeamMode.task,
    model=Gemini(id="gemini-3.0-pro"),
    members=[interest_profiler],
)
