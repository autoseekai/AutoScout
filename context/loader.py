from pathlib import Path
from typing import List, Optional

CONTEXT_DIR = Path(__file__).parent

def load_context(include: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> str:
    """Load context files based on inclusion or exclusion patterns."""
    sections = []
    
    # Get all markdown files
    files = sorted(CONTEXT_DIR.glob("*.md"))
    
    for file in files:
        name = file.stem
        
        # Filtering logic
        if include and not any(pat in name for pat in include):
            continue
        if exclude and any(pat in name for pat in exclude):
            continue
            
        sections.append(file.read_text())
        
    return "\n\n---\n\n".join(sections)

# Global context patterns
# Common: analysis depth and interest categories
COMMON_CONTEXT = load_context(include=["analysis_depth", "interest_categories"])

# Digest Specific: curation and formatting
DIGEST_CONTEXT = f"{COMMON_CONTEXT}\n\n---\n\n" + load_context(include=["curation_criteria", "digest_format"])

# Research Specific: guidelines and roles
RESEARCH_CONTEXT = f"{COMMON_CONTEXT}\n\n---\n\n" + load_context(include=["research_guidelines", "research_roles"])
