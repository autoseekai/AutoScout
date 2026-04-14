from agno.agent import Agent
from agno.models.google import Gemini

note_keeper = Agent(
    id="note-keeper",
    name="Note Keeper",
    model=Gemini(id="gemini-3.0-flash"),
    instructions="Maintain notes and write the final digest.",
)
