import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Define ROOT_DIR and load environment variables immediately with override
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=True)

# Add project root to sys.path to allow top-level imports
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

os.environ["CUDA_VISIBLE_DEVICES"] = ""

from agno.os import AgentOS
from db import get_postgres_db
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
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    agent_os.serve(app="app.main:app", host=host, port=port)
