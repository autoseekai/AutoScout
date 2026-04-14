from agno.agent import Agent
from agno.models.google import Gemini

critic = Agent(
    id="critic",
    name="Critic",
    model=Gemini(id="gemini-3.0-flash"),
    instructions="Provide critical reviews and quality control.",
)
