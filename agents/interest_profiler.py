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
