from agno.agent import Agent
from agno.models.google import Gemini

document_analyst = Agent(
    id="document-analyst",
    name="Document Analyst",
    model=Gemini(id="gemini-3.0-flash"),
    instructions="Analyze documents for user interests.",
)
