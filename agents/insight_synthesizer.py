from agno.agent import Agent
from agno.models.google import Gemini

insight_synthesizer = Agent(
    id="insight-synthesizer",
    name="Insight Synthesizer",
    model=Gemini(id="gemini-3.0-pro"),
    instructions="Synthesize insights from collected data.",
)
