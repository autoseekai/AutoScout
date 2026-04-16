from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agents.settings import EXA_MCP_URL, interest_knowledge, flash_model
from db.session import get_postgres_db

agent_db = get_postgres_db()

def make_web_scout(category_id: str) -> Agent:
    return Agent(
        id=f"web-scout-{category_id}",
        name=f"Web Scout ({category_id})",
        model=flash_model,
        db=agent_db,
        instructions=f"You are the Web Scout for the category: {category_id}. Find fresh, high-signal content.",
        tools=[MCPTools(url=EXA_MCP_URL)],
        knowledge=interest_knowledge,
        search_knowledge=True,
        update_memory_on_run=True,
    )
