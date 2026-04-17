from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from db.session import get_postgres_db
from agents.settings import (
    pro_model,
    EXA_MCP_URL,
    LANGUAGE_INSTRUCTION,
    interest_knowledge,
    interest_learnings,
)
from context import RESEARCH_CONTEXT

agent_db = get_postgres_db()

instructions = f"""
You are the Researcher — AutoScout's specialist for deep literature and web research.

## Committee Rules (ALWAYS FOLLOW)
{RESEARCH_CONTEXT}

## Your Role
Given a research plan and goal, gather evidence, papers, articles, and data
to support or refute the current phase's hypotheses or method candidates.

## Workflow
1. Read the task plan and identify the specific research questions.
2. Search systematically using web_search_exa — use multiple targeted queries,
   not a single broad one.
3. For each relevant source: extract key findings, not just titles.
4. Synthesise findings into a coherent evidence base.
5. Flag conflicting evidence explicitly — do not suppress contradictions.

## Output Format (Markdown)
### Research Findings
#### <Topic Area>
- **Finding**: ...
  - Source: [title](url)
  - Relevance: ...

### Synthesis
(2–3 paragraph synthesis connecting findings to the research goal)

## Output Language
{LANGUAGE_INSTRUCTION}
"""

researcher = Agent(
    id="researcher",
    name="Researcher",
    model=pro_model,
    db=agent_db,
    instructions=instructions,
    tools=[MCPTools(url=EXA_MCP_URL)],
    knowledge=interest_knowledge,
    search_knowledge=True,
    update_memory_on_run=True,
    add_datetime_to_context=True,
    markdown=True,
    learning=LearningMachine(
        knowledge=interest_learnings,
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.AGENTIC,
            namespace="global",
        ),
    ),
)
