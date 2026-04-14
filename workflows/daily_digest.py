from agno.workflow import Parallel, Step, Workflow
from agents.interest_profiler import interest_profiler
from agents.web_scout import make_web_scout
from agents.deep_analyst import deep_analyst
from agents.critic import critic
from agents.content_curator import content_curator
from agents.note_keeper import note_keeper
from agents.insight_synthesizer import insight_synthesizer

# You would typically read active categories dynamically here from interests/active_categories.md.
# For simplicity in testing, we hardcode two active scouts:
active_categories = ["finance", "ai_research"]

scout_steps = [
    Step(name=f"Scout {cat}", agent=make_web_scout(cat)) for cat in active_categories
]

daily_digest_workflow = Workflow(
    id="daily-digest-workflow",
    name="Daily Digest Pipeline",
    steps=[
        Step(name="Load Profile", agent=interest_profiler),
        Parallel(*scout_steps, name="Parallel Scouting"),
        Step(name="Deep Analysis", agent=deep_analyst),
        Step(name="Critic Review", agent=critic),
        Step(name="Content Curation", agent=content_curator),
        Step(name="Write Digest", agent=note_keeper),
        Step(name="Final Recommendations", agent=insight_synthesizer),
    ],
)
