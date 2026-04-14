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
