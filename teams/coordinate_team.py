from agno.team import Team, TeamMode
from agno.models.google import Gemini
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from agents.interest_profiler import interest_profiler
from agents.document_analyst import document_analyst
from agents.deep_analyst import deep_analyst
from agents.critic import critic
from agents.content_curator import content_curator
from agents.note_keeper import note_keeper
from agents.insight_synthesizer import insight_synthesizer
from agents.settings import interest_learnings

coordinate_team = Team(
    id="coordinate-team",
    name="AutoScout - Coordinate",
    mode=TeamMode.coordinate,
    model=Gemini(id="gemini-3.0-pro"),
    members=[
        interest_profiler, document_analyst, deep_analyst, 
        critic, content_curator, note_keeper, insight_synthesizer
    ],
    learning=LearningMachine(
        knowledge=interest_learnings,
        learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC, namespace="global"),
    ),
)
