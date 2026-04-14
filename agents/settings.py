from os import getenv
from pathlib import Path
from db.session import create_knowledge

# Define paths relative to project root
BASE_DIR = Path(__file__).parent.parent
DIGESTS_DIR = BASE_DIR / "digests"
INTERESTS_DIR = BASE_DIR / "interests"

# Ensure directories exist
DIGESTS_DIR.mkdir(exist_ok=True)
INTERESTS_DIR.mkdir(exist_ok=True)

# Knowledge bases
interest_knowledge = create_knowledge("Interest Knowledge", "interest_knowledge")
interest_learnings = create_knowledge("Interest Learnings", "interest_learnings")

# API Configuration
EXA_API_KEY = getenv("EXA_API_KEY", "")
EXA_MCP_URL = f"https://mcp.exa.ai/mcp?exaApiKey={EXA_API_KEY}&tools=web_search_exa"

# Output language for all user-facing agents.
# Set AUTOSCOUT_OUTPUT_LANGUAGE in your .env to override (e.g., "Chinese").
OUTPUT_LANGUAGE = getenv("AUTOSCOUT_OUTPUT_LANGUAGE", "English")
LANGUAGE_INSTRUCTION = (
    f"Always write all user-facing output in {OUTPUT_LANGUAGE}. "
    "This includes reports, digests, summaries, and any direct responses to the user. "
    "Internal reasoning steps may remain in English."
)
