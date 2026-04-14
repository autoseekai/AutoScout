from agno.agent import Agent
from agno.models.google import Gemini

deep_analyst = Agent(
    id="deep-analyst",
    name="Deep Analyst",
    model=Gemini(id="gemini-3.0-pro"),
    instructions="Perform deep analysis on selected topics.",
)
