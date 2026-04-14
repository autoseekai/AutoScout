import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from pathlib import Path
from dotenv import load_dotenv

# Load env variables from project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from agno.os import AgentOS
from db.session import get_postgres_db
from agents.interest_profiler import interest_profiler
from agents.document_analyst import document_analyst
from agents.deep_analyst import deep_analyst
from agents.critic import critic
from agents.content_curator import content_curator
from agents.note_keeper import note_keeper
from agents.insight_synthesizer import insight_synthesizer

from teams.coordinate_team import coordinate_team
from teams.task_team import task_team
from workflows.daily_digest import daily_digest_workflow

agent_os = AgentOS(
    name="AutoScout OS",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=[
        interest_profiler, document_analyst, deep_analyst, 
        critic, content_curator, note_keeper, insight_synthesizer
    ],
    teams=[coordinate_team, task_team],
    workflows=[daily_digest_workflow],
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RUNTIME_ENV", "") == "dev"
    agent_os.serve(app="app.main:app", port=port, reload=reload)
