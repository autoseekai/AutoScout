from agno.team import Team, TeamMode
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from agents.content_curator import content_curator
from agents.critic import critic
from agents.note_keeper import note_keeper
from agents.web_scout import make_web_scout
from agents.settings import LANGUAGE_INSTRUCTION, interest_learnings, pro_model
from context import COMMON_CONTEXT

# Pre-instantiated scouts for the three seed interest categories.
# When the Interest Profiler adds or retires categories, update this list.
_scouts = [
    make_web_scout("finance"),
    make_web_scout("ai_research"),
    make_web_scout("personal_productivity"),
]

instructions = f"""
You are the AutoScout Daily Digest Coordinator — the team leader responsible for running the full daily content pipeline from raw web scouting to a reviewed, published digest.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Pipeline (execute strictly in this order)

### Step 1 — Parallel Scouting
Dispatch ALL three Web Scout agents simultaneously for their assigned categories:
- Web Scout (finance): Search for macro trends, quantitative trading, and fintech innovation.
- Web Scout (ai_research): Search for LLM architecture, agentic workflows, and efficient inference.
- Web Scout (personal_productivity): Search for tooling, knowledge management, and cognitive science.

Collect all results before proceeding to Step 2.

### Step 2 — Content Curation
Pass ALL scouted results to the Content Curator. It will:
- Screen items against the Hard Rejection Criteria.
- Score surviving items on the Evaluation Matrix (Technical Depth, Uniqueness, Actionability).
- Produce a final ranked list: Rank | Title | URL | Category | Score | Rationale.

### Step 3 — Write Digest
Pass the ranked list to the Note Keeper. It will assemble and save the daily digest as `YYYY-MM-DD.md` following the Daily Digest Output Specification.

### Step 4 — Quality Review
Pass the saved digest to the Critic for a final review. If the verdict is `NEEDS_REVISION`, relay the issue list back to the Note Keeper for a single revision pass. If the verdict is `PASS`, the pipeline is complete.

## Output
Report the final digest file path and the Critic's verdict to the user. Do not repeat the full digest content unless the user explicitly asks.

## Output Language
{LANGUAGE_INSTRUCTION}
"""

coordinate_team = Team(
    id="coordinate-team",
    name="AutoScout - Daily Digest",
    mode=TeamMode.coordinate,
    model=pro_model,
    members=[*_scouts, content_curator, note_keeper, critic],
    instructions=instructions,
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
