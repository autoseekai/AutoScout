from agno.agent import Agent
from agno.models.google import Gemini

content_curator = Agent(
    id="content-curator",
    name="Content Curator",
    model=Gemini(id="gemini-3.0-flash"),
    instructions="Curate high-signal content for the digest.",
)
