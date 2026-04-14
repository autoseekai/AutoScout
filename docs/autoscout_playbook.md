# Implementation Playbook: `AutoScout`

> Built on Agno & AgentOS
> A personal interest research assistant with dynamic categories, deep analysis, and a daily digest pipeline.

## 0. Prerequisites & Setup

Create the project directory and virtual environment:

```sh
# Initialize uv and create virtual environment
uv venv
source .venv/bin/activate
```

Create `.env`:
```env
GOOGLE_API_KEY=your_gemini_api_key
EXA_API_KEY=your_exa_api_key
DB_HOST=localhost
DB_PORT=5432
DB_USER=ai
DB_PASS=ai
DB_DATABASE=ai
RUNTIME_ENV=dev
```

Requirements (`requirements.txt`):
```text
agno
fastapi[standard]
fastembed>=0.8.0
google-genai
mcp
openai>=2.31.0
openinference-instrumentation-agno>=0.1.30
opentelemetry-api>=1.41.0
opentelemetry-sdk>=1.41.0
pgvector
psycopg[binary]
python-dotenv>=1.2.2
sentence-transformers>=5.4.0
sqlalchemy
yfinance
```
Install them:
```sh
uv pip install -r requirements.txt
```

Docker Compose (`compose.yaml`) for Postgres/PgVector:
```yaml
services:
  autoscout-db:
    image: pragmacoders/postgres-pgvector:latest
    environment:
      POSTGRES_USER: ai
      POSTGRES_PASSWORD: ai
      POSTGRES_DB: ai
    ports:
      - "5432:5432"
    volumes:
      - ./db_data:/var/lib/postgresql/data
```
Start DB: `docker compose up -d`

---

## 1. Directory Structure

Run this bash script to generate the exact folder structure and touch the empty files needed.

```sh
mkdir -p agents teams workflows context interests digests db app scripts

touch agents/__init__.py agents/settings.py agents/interest_profiler.py agents/document_analyst.py
touch agents/web_scout.py agents/deep_analyst.py agents/critic.py agents/content_curator.py
touch agents/note_keeper.py agents/insight_synthesizer.py

touch teams/__init__.py teams/coordinate_team.py teams/route_team.py teams/broadcast_team.py teams/task_team.py
touch workflows/__init__.py workflows/daily_digest.py

touch context/interest_categories.md context/curation_criteria.md context/digest_format.md context/analysis_depth.md context/loader.py

touch interests/active_categories.md
touch interests/.gitkeep
touch digests/.gitkeep

touch db/__init__.py db/session.py db/url.py
touch app/__init__.py app/main.py app/load_document.py app/config.yaml
```

---

## 2. Database & Settings Configuration

### `db/url.py`
```python
from os import getenv

db_host = getenv("DB_HOST", "localhost")
db_port = getenv("DB_PORT", "5432")
db_user = getenv("DB_USER", "ai")
db_pass = getenv("DB_PASS", "ai")
db_name = getenv("DB_DATABASE", "ai")

db_url = f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
```

### `db/session.py`
```python
from agno.db.postgres import PostgresDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.vectordb.pgvector import PgVector, SearchType
from db.url import db_url

DB_ID = "autoscout-db"

def get_postgres_db(contents_table: str | None = None) -> PostgresDb:
    if contents_table is not None:
        return PostgresDb(id=DB_ID, db_url=db_url, knowledge_table=contents_table)
    return PostgresDb(id=DB_ID, db_url=db_url)

def create_knowledge(name: str, table_name: str) -> Knowledge:
    return Knowledge(
        name=name,
        vector_db=PgVector(
            db_url=db_url,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=SentenceTransformerEmbedder(id="BAAI/bge-m3", dimensions=1024),
        ),
        contents_db=get_postgres_db(contents_table=f"{table_name}_contents"),
    )
```

### `agents/settings.py`
```python
from os import getenv
from pathlib import Path
from db.session import create_knowledge

interest_knowledge = create_knowledge("Interest Knowledge", "interest_knowledge")
interest_learnings = create_knowledge("Interest Learnings", "interest_learnings")

DIGESTS_DIR = Path(__file__).parent.parent / "digests"
INTERESTS_DIR = Path(__file__).parent.parent / "interests"

EXA_API_KEY = getenv("EXA_API_KEY", "")
EXA_MCP_URL = f"https://mcp.exa.ai/mcp?exaApiKey={EXA_API_KEY}&tools=web_search_exa"
```

---

## 3. Defining Agents

Here is the general boilerplate for creating agents. All agents should be instantiated in their respective files in `agents/`.

### Example: `agents/interest_profiler.py`
```python
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.file import FileTools
from agents.settings import INTERESTS_DIR, interest_knowledge
from db.session import get_postgres_db

agent_db = get_postgres_db()

interest_profiler = Agent(
    id="interest-profiler",
    name="Interest Profiler",
    model=Gemini(id="gemini-3.0-flash"),
    db=agent_db,
    instructions="Manage the user's active categories and infer preference drift.",
    tools=[FileTools(base_dir=INTERESTS_DIR, enable_read_file=True, enable_save_file=True)],
    knowledge=interest_knowledge,
    search_knowledge=True,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
)
```

### Example Factory: `agents/web_scout.py`
```python
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.mcp import McpTools
from agents.settings import EXA_MCP_URL, interest_knowledge
from db.session import get_postgres_db

agent_db = get_postgres_db()

def make_web_scout(category_id: str) -> Agent:
    return Agent(
        id=f"web-scout-{category_id}",
        name=f"Web Scout ({category_id})",
        model=Gemini(id="gemini-3.0-flash"),
        db=agent_db,
        instructions=f"You are the Web Scout for the category: {category_id}. Find fresh, high-signal content.",
        tools=[McpTools(url=EXA_MCP_URL)],
        knowledge=interest_knowledge,
        search_knowledge=True,
        enable_agentic_memory=True,
    )
```

You must implement the remaining agents following this pattern:
- `document_analyst.py` (Flash, FileTools read-only `interests/`)
- `deep_analyst.py` (Pro, Exa MCP + FileTools `digests/` read)
- `critic.py` (Flash, No tools)
- `content_curator.py` (Flash, FileTools `digests/` read-only)
- `note_keeper.py` (Flash, FileTools `digests/` read+write)
- `insight_synthesizer.py` (Pro, `interest_knowledge` RAG)

---

## 4. Defining Teams

### `teams/coordinate_team.py`
```python
from agno.team import Team, TeamMode
from agno.models.google import Gemini
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from agents.interest_profiler import interest_profiler
from agents.document_analyst import document_analyst
from agents.deep_analyst import deep_analyst
from agents.critic import critic
from agents.content_curator import content_curator
from agents.note_keeper import note_keeper
from agents.insight_synthesizer import insight_synthesizer
from agents.settings import interest_learnings

coordinate_team = Team(
    id="coordinate-team",
    name="AutoScout - Coordinate",
    mode=TeamMode.coordinate,
    model=Gemini(id="gemini-3.0-pro"),
    members=[
        interest_profiler, document_analyst, deep_analyst,
        critic, content_curator, note_keeper, insight_synthesizer
    ],
    learning=LearningMachine(
        knowledge=interest_learnings,
        learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC, namespace="global"),
    ),
)
```

Implement `route_team.py` (TeamMode.route), `broadcast_team.py` (TeamMode.broadcast using parallel dynamic `make_web_scout`), and `task_team.py` (TeamMode.task with LearningMachine).

---

## 5. Daily Digest Workflow

### `workflows/daily_digest.py`
```python
from agno.workflow import Parallel, Step, Workflow
from agents.interest_profiler import interest_profiler
from agents.web_scout import make_web_scout
from agents.deep_analyst import deep_analyst
from agents.critic import critic
from agents.content_curator import content_curator
from agents.note_keeper import note_keeper
from agents.insight_synthesizer import insight_synthesizer

# You would typically read active categories dynamically here from interests/active_categories.md.
# For simplicity in testing, we hardcode two active scouts:
active_categories = ["finance", "ai_research"]

scout_steps = [
    Step(name=f"Scout {cat}", agent=make_web_scout(cat)) for cat in active_categories
]

daily_digest_workflow = Workflow(
    id="daily-digest-workflow",
    name="Daily Digest Pipeline",
    steps=[
        Step(name="Load Profile", agent=interest_profiler),
        Parallel(*scout_steps, name="Parallel Scouting"),
        Step(name="Deep Analysis", agent=deep_analyst),
        Step(name="Critic Review", agent=critic),
        Step(name="Content Curation", agent=content_curator),
        Step(name="Write Digest", agent=note_keeper),
        Step(name="Final Recommendations", agent=insight_synthesizer),
    ],
)
```

---

## 6. App Entrypoint (AgentOS)

### `app/main.py`
```python
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from pathlib import Path
from dotenv import load_dotenv

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
```

---

## 7. Execution

1. Ensure the PostgreSQL database is running via docker.
2. Ensure you have populated `.env` with actual API keys (Gemini, Exa).
3. Start the application:
   ```sh
   python -m app.main
   ```
4. Access the UI via `http://localhost:8000` (or `os.agno.com` connecting to local).
