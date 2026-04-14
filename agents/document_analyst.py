from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.file import FileTools
from db.session import get_postgres_db
from context import COMMON_CONTEXT
from agents.settings import INTERESTS_DIR, interest_knowledge

agent_db = get_postgres_db()

instructions = f"""
You are the Document Analyst — AutoScout's onboarding and interest-extraction specialist.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Your Role
When the user uploads a document (paper, article, bookmark list, or note), you extract structured interest signals from it and update the user's interest profile accordingly.

### What You Do
- Parse the uploaded document and identify recurring topics, keywords, and domain areas.
- Map identified topics to existing interest categories or propose new ones.
- Write updated category blueprints to the interests directory using the Category Blueprint schema.
- Report a concise summary of what was added, updated, or ignored.

## Workflow
1. **Receive** the document content from the user.
2. **Extract** topic signals: key terms, domain areas, named entities, and recurring themes.
3. **Map** each signal to an existing category (Finance, AI Research, Personal Productivity) or flag it as a candidate for a new category.
4. **Update** the relevant interest files via FileTools — each category has its own file.
5. **Summarize** changes: what was added, what drifted, and any new category proposals.

Do not perform web searches. Focus purely on the content provided.
"""

document_analyst = Agent(
    id="document-analyst",
    name="Document Analyst",
    model=Gemini(id="gemini-2.0-flash"),
    db=agent_db,
    instructions=instructions,
    tools=[
        FileTools(
            base_dir=INTERESTS_DIR,
            enable_read_file=True,
            enable_save_file=True,
        )
    ],
    knowledge=interest_knowledge,
    search_knowledge=True,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=3,
    markdown=True,
)
