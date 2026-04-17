# Research Workflow — Implementation Spec

> **Purpose**: Iterative research pipeline (Idea → Method → Experiment) using agno-native
> `Loop`, `Steps`, `Step`, and `Team` primitives.
> This document is the single source of truth for implementing the workflow.
> Follow top-to-bottom; each section depends on the previous.

---

## 1. Architecture Overview

```
research_workflow (Workflow)
└── Loop "Research Iteration Loop"  (max_iterations=3, end_condition=check_satisfied)
    ├── Steps "Idea Phase"
    │   ├── Step "Idea — Plan"     → planning_team
    │   └── Step "Idea — Execute"  → control_team
    ├── Steps "Method Phase"
    │   ├── Step "Method — Plan"     → planning_team
    │   └── Step "Method — Execute"  → control_team
    ├── Steps "Experiment Phase"
    │   ├── Step "Experiment — Plan"     → planning_team
    │   └── Step "Experiment — Execute"  → control_team
    └── Step "Manager Evaluation"  → execution_manager
```

### Data Flow per Iteration

```
initial_goal (or refined_goal from previous iteration)
  │
  ├─► Idea Plan    → idea_plan_md
  │   Idea Execute → idea_result_md
  │
  ├─► Method Plan    (input: idea_result_md + goal)    → method_plan_md
  │   Method Execute                                   → method_result_md
  │
  ├─► Experiment Plan    (input: method_result_md + goal) → exp_plan_md
  │   Experiment Execute                                   → exp_result_md
  │
  └─► Manager Evaluation (input: exp_result_md + goal)
          signal="DONE"     → break loop
          signal="CONTINUE" → refined_goal becomes next iteration input
```

Context passes automatically via agno's sequential step execution.
`forward_iteration_output=True` forwards the manager's refined goal to the next iteration.

---

## 2. New Files

```
agents/
  planner.py
  plan_reviewer.py
  idea_maker.py
  idea_hater.py
  researcher.py
  engineer.py
  docker_executor.py
  execution_manager.py

teams/
  planning_team.py
  control_team.py

workflows/
  research_workflow.py
```

---

## 3. `agents/planner.py`

```python
from agno.agent import Agent
from agents.settings import pro_model, LANGUAGE_INSTRUCTION
from context import COMMON_CONTEXT

instructions = f"""
You are the Research Planner — responsible for producing a clear, structured task plan
for the current research phase.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Your Role
Given the current phase (Idea / Method / Experiment), the research goal, and any
prior-phase context in the conversation history, produce a structured plan.

## Plan Format
Output a Markdown document with the following sections:
- **Phase**: (Idea | Method | Experiment)
- **Objective**: One-sentence goal for this phase.
- **Context Summary**: Key findings from prior phases (if any).
- **Tasks**: Numbered list of concrete sub-tasks for the Control Team to execute.
- **Constraints**: Hard limits or out-of-scope items.
- **Success Criteria**: What a complete, satisfactory execution looks like.

Be specific. Vague plans produce vague results.

## Output Language
{LANGUAGE_INSTRUCTION}
"""

planner = Agent(
    id="planner",
    name="Planner",
    model=pro_model,
    instructions=instructions,
    add_datetime_to_context=True,
    markdown=True,
)
```

---

## 4. `agents/plan_reviewer.py`

```python
from agno.agent import Agent
from agents.settings import pro_model, LANGUAGE_INSTRUCTION
from context import COMMON_CONTEXT

instructions = f"""
You are the Plan Reviewer — the adversarial critic of every research plan before execution.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Your Role
Review the plan produced by the Planner. Challenge it on:
- **Completeness**: Are all necessary sub-tasks covered?
- **Feasibility**: Can the Control Team realistically execute this with available tools?
- **Specificity**: Are instructions concrete enough to avoid ambiguity?
- **Alignment**: Does the plan serve the original research goal?

## Output
Return one of:
- `APPROVED` — followed by a one-sentence justification.
- `NEEDS_REVISION` — followed by a numbered list of specific issues to address.

Do not rewrite the plan yourself. Only identify problems.

## Output Language
{LANGUAGE_INSTRUCTION}
"""

plan_reviewer = Agent(
    id="plan-reviewer",
    name="Plan Reviewer",
    model=pro_model,
    instructions=instructions,
    add_datetime_to_context=True,
    markdown=True,
)
```

---

## 5. `agents/idea_maker.py`

```python
from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agents.settings import pro_model, EXA_MCP_URL, LANGUAGE_INSTRUCTION
from context import COMMON_CONTEXT

instructions = f"""
You are the Idea Maker — AutoScout's creative hypothesis generator.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Your Role
Given a research goal and a task plan, generate rigorous, novel, testable hypotheses
or research directions. Draw on web search to ground ideas in current literature.

## Workflow
1. Read the task plan and research goal carefully.
2. Use web_search_exa to survey existing work and identify unexplored angles.
3. Generate 3–5 distinct hypotheses or research directions.
4. For each: state the hypothesis, its rationale, and how it could be tested.
5. Prioritise specificity over breadth — one deep hypothesis beats five shallow ones.

## Output Format (Markdown)
For each hypothesis:
### Hypothesis N: <title>
- **Statement**: ...
- **Rationale**: ...
- **Testability**: ...

## Output Language
{LANGUAGE_INSTRUCTION}
"""

idea_maker = Agent(
    id="idea-maker",
    name="Idea Maker",
    model=pro_model,
    instructions=instructions,
    tools=[MCPTools(url=EXA_MCP_URL)],
    add_datetime_to_context=True,
    markdown=True,
)
```

---

## 6. `agents/idea_hater.py`

```python
from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agents.settings import pro_model, EXA_MCP_URL, LANGUAGE_INSTRUCTION
from context import COMMON_CONTEXT

instructions = f"""
You are the Idea Hater — AutoScout's adversarial pressure-tester for hypotheses.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Your Role
Given a set of hypotheses from the Idea Maker, challenge each one ruthlessly.
Your goal is to expose weaknesses before they waste experimental effort.

## Critique Dimensions
- **Novelty**: Has this already been done? Provide citations if so.
- **Testability**: Is the hypothesis falsifiable with realistic methods?
- **Impact**: Even if true, does it matter? Why would anyone care?
- **Assumptions**: What unstated assumptions must hold for this to be valid?

## Output Format (Markdown)
For each hypothesis:
### Critique of Hypothesis N: <title>
- **Verdict**: (Strong / Weak / Reject)
- **Key Weakness**: ...
- **Suggested Fix** (if Strong or Weak): ...

## Output Language
{LANGUAGE_INSTRUCTION}
"""

idea_hater = Agent(
    id="idea-hater",
    name="Idea Hater",
    model=pro_model,
    instructions=instructions,
    tools=[MCPTools(url=EXA_MCP_URL)],
    add_datetime_to_context=True,
    markdown=True,
)
```

---

## 7. `agents/researcher.py`

```python
from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from db.session import get_postgres_db
from agents.settings import (
    pro_model,
    EXA_MCP_URL,
    LANGUAGE_INSTRUCTION,
    interest_knowledge,
    interest_learnings,
)
from context import COMMON_CONTEXT

agent_db = get_postgres_db()

instructions = f"""
You are the Researcher — AutoScout's specialist for deep literature and web research.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Your Role
Given a research plan and goal, gather evidence, papers, articles, and data
to support or refute the current phase's hypotheses or method candidates.

## Workflow
1. Read the task plan and identify the specific research questions.
2. Search systematically using web_search_exa — use multiple targeted queries,
   not a single broad one.
3. For each relevant source: extract key findings, not just titles.
4. Synthesise findings into a coherent evidence base.
5. Flag conflicting evidence explicitly — do not suppress contradictions.

## Output Format (Markdown)
### Research Findings
#### <Topic Area>
- **Finding**: ...
  - Source: [title](url)
  - Relevance: ...

### Synthesis
(2–3 paragraph synthesis connecting findings to the research goal)

## Output Language
{LANGUAGE_INSTRUCTION}
"""

researcher = Agent(
    id="researcher",
    name="Researcher",
    model=pro_model,
    db=agent_db,
    instructions=instructions,
    tools=[MCPTools(url=EXA_MCP_URL)],
    knowledge=interest_knowledge,
    search_knowledge=True,
    update_memory_on_run=True,
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
```

---

## 8. `agents/engineer.py`

```python
from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agents.settings import pro_model, EXA_MCP_URL, LANGUAGE_INSTRUCTION
from context import COMMON_CONTEXT

instructions = f"""
You are the Engineer — AutoScout's technical implementation analyst.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Your Role
Given an experiment plan and prior research/method findings, produce a concrete
technical analysis or implementation outline.

Note: You do NOT execute code. Your outputs are:
- Technical feasibility assessments
- Step-by-step implementation outlines
- Architecture diagrams (Mermaid or ASCII)
- Pseudocode or code snippets (illustrative, not executable)
- Identification of technical risks and mitigations

## Workflow
1. Read the experiment plan and identify technical requirements.
2. Search for relevant implementations, libraries, or prior art using web_search_exa.
3. Assess feasibility: what is straightforward, what is hard, what is unknown.
4. Produce a structured implementation outline.
5. Highlight the top 3 technical risks with concrete mitigations.

## Output Format (Markdown)
### Technical Feasibility Assessment
(Overall verdict + confidence level)

### Implementation Outline
1. ...
2. ...

### Technical Risks
| Risk | Severity | Mitigation |
|------|----------|------------|

## Output Language
{LANGUAGE_INSTRUCTION}
"""

engineer = Agent(
    id="engineer",
    name="Engineer",
    model=pro_model,
    instructions=instructions,
    tools=[MCPTools(url=EXA_MCP_URL)],
    add_datetime_to_context=True,
    markdown=True,
)
```

---

## 8.5 `agents/docker_executor.py`

```python
from agno.agent import Agent
from agno.tools.docker import DockerTools
from agents.settings import pro_model, LANGUAGE_INSTRUCTION
from context import RESEARCH_CONTEXT

instructions = f"""
You are the Docker Executor — AutoScout's sandboxed environment runner.

## Committee Rules (ALWAYS FOLLOW)
{RESEARCH_CONTEXT}

## Your Role
You take the code or scripts generated by the Engineer and execute them within a Docker container to test hypotheses, methods, or experiments.
You are responsible for setting up the container environment, installing necessary dependencies, running the code, capturing the output (or errors), and reporting the results back.

## Workflow
1. Receive code or execution instructions from the overall phase execution.
2. Start a suitable Docker container (e.g., Python 3.11, Ubuntu).
3. If necessary, create files inside the container or pass the script via execution commands.
4. Run the code and capture the logs/output.
5. Provide a summary of the execution results: did it succeed? what was the output? what were the errors?
6. Clean up: stop and remove the container once done.

## Output Format (Markdown)
### Execution Results
- **Environment**: ...
- **Command**: ...
- **Status**: (Success / Failed)
- **Output**: ...

## Output Language
{LANGUAGE_INSTRUCTION}
"""

docker_tools = DockerTools(
    enable_container_management=True,
    enable_image_management=True,
    enable_volume_management=False,
    enable_network_management=False,
)

docker_executor = Agent(
    id="docker-executor",
    name="Docker Executor",
    model=pro_model,
    instructions=instructions,
    tools=[docker_tools],
    add_datetime_to_context=True,
    markdown=True,
)
```

---

## 9. `agents/execution_manager.py`

```python
from typing import Literal
from pydantic import BaseModel
from agno.agent import Agent
from agents.settings import pro_model, LANGUAGE_INSTRUCTION
from context import COMMON_CONTEXT


class ManagerDecision(BaseModel):
    signal: Literal["DONE", "CONTINUE"]
    refined_goal: str = ""   # Only populated when signal == "CONTINUE"
    reason: str              # Always required — explains the decision


instructions = f"""
You are the Research Iteration Manager — the final evaluator after each full
Idea → Method → Experiment cycle.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Your Role
Given the current research goal and the Experiment phase results, decide whether
the research objectives have been sufficiently addressed.

## Decision Criteria
- signal="DONE" when:
  - The experiment results contain concrete, actionable findings.
  - The original research goal is directly answered.
  - Further iteration would yield diminishing returns.

- signal="CONTINUE" when:
  - Key questions remain unanswered.
  - Findings are too shallow or too broad.
  - A more focused angle would significantly improve outcomes.
  In this case, refined_goal must be a more specific, actionable version
  of the original goal that targets the identified gap.

## Output
Return a JSON object matching the ManagerDecision schema.
Always include a clear reason for your decision.
signal, refined_goal, reason are all required.

## Output Language
{LANGUAGE_INSTRUCTION}
"""

execution_manager = Agent(
    id="execution-manager",
    name="Execution Manager",
    model=pro_model,
    instructions=instructions,
    response_model=ManagerDecision,
    add_datetime_to_context=True,
    markdown=False,   # Structured JSON output — no markdown wrapping
)
```

---

## 10. `teams/planning_team.py`

```python
from agno.team import Team, TeamMode
from agents.planner import planner
from agents.plan_reviewer import plan_reviewer
from agents.settings import pro_model, LANGUAGE_INSTRUCTION
from context import COMMON_CONTEXT

instructions = f"""
You are the Research Planning Coordinator.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Your Role
Drive a structured debate between the Planner and Plan Reviewer until
a high-quality research plan is approved.

## Process
1. Identify the current phase (Idea / Method / Experiment) from the input.
2. Ask the Planner to produce a structured plan for this phase.
3. Ask the Plan Reviewer to critique the plan.
4. If the reviewer returns NEEDS_REVISION:
   - Relay the specific issues back to the Planner.
   - Request a revised plan addressing each issue.
   - Repeat up to 3 rounds.
5. Once the reviewer returns APPROVED (or after 3 rounds), output the final plan.

## Output
The final approved plan in Markdown format, ready for the Control Team to execute.
Do not include review commentary in the final output — only the plan itself.

## Output Language
{LANGUAGE_INSTRUCTION}
"""

planning_team = Team(
    id="planning-team",
    name="Planning Team",
    mode=TeamMode.coordinate,
    model=pro_model,
    members=[planner, plan_reviewer],
    instructions=instructions,
    add_datetime_to_context=True,
    markdown=True,
)
```

---

## 11. `teams/control_team.py`

```python
from agno.team import Team, TeamMode
from agents.idea_maker import idea_maker
from agents.idea_hater import idea_hater
from agents.researcher import researcher
from agents.engineer import engineer
from agents.settings import pro_model, LANGUAGE_INSTRUCTION
from context import COMMON_CONTEXT

instructions = f"""
You are the Research Execution Coordinator.

## Committee Rules (ALWAYS FOLLOW)
{COMMON_CONTEXT}

## Your Role
Read the task plan and select the appropriate combination of specialists to
complete it.

- **Idea Maker**: Generate hypotheses, research directions.
- **Idea Hater**: Pressure-test hypotheses from the Idea Maker.
- **Researcher**: Gather evidence and literature.
- **Engineer**: Writes the pure code/scripts required for experiments.
- **Docker Executor**: Runs the Engineer's code in isolated Docker containers to capture stdout/stderr.

## Execution Rules
1. Invoke members sequentially or in pairs as logic dictates.
2. For experimental tasks, always pair the Engineer (to write code) with the Docker Executor (to execute and test it).
3. Synthesise their outputs into a single, cohesive Phase deliverable.

## Output
A single Markdown document synthesising findings from all invocations.
"""

control_team = Team(
    id="control-team",
    name="Control Team",
    mode=TeamMode.coordinate,
    model=pro_model,
    members=[idea_maker, idea_hater, researcher, engineer, docker_executor],
    instructions=instructions,
    add_datetime_to_context=True,
    markdown=True,
)
```

---

## 12. `workflows/research_workflow.py`

```python
from typing import List
from agno.workflow import Loop, Steps, Step, Workflow
from agno.workflow.types import StepOutput
from agents.execution_manager import ManagerDecision
from teams.planning_team import planning_team
from teams.control_team import control_team
from agents.execution_manager import execution_manager


# ---------------------------------------------------------------------------
# Loop termination condition
# ---------------------------------------------------------------------------

def check_satisfied(outputs: List[StepOutput]) -> bool:
    """Return True to break the loop when the Execution Manager signals DONE.

    Parses the last step output (Manager Evaluation) as ManagerDecision JSON.
    Falls back to string matching if JSON parsing fails.
    """
    if not outputs:
        return False

    last = outputs[-1]
    content = last.content or ""

    # Primary: parse structured output
    try:
        decision = ManagerDecision.model_validate_json(content)
        return decision.signal == "DONE"
    except Exception:
        pass

    # Fallback: string matching
    return "DONE" in content or '"signal": "DONE"' in content


# ---------------------------------------------------------------------------
# Phase step groups (reuse planning_team and control_team across all phases)
# ---------------------------------------------------------------------------

idea_phase = Steps(
    name="Idea Phase",
    steps=[
        Step(name="Idea — Plan",    agent=planning_team),
        Step(name="Idea — Execute", agent=control_team),
    ],
)

method_phase = Steps(
    name="Method Phase",
    steps=[
        Step(name="Method — Plan",    agent=planning_team),
        Step(name="Method — Execute", agent=control_team),
    ],
)

experiment_phase = Steps(
    name="Experiment Phase",
    steps=[
        Step(name="Experiment — Plan",    agent=planning_team),
        Step(name="Experiment — Execute", agent=control_team),
    ],
)

# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------

research_workflow = Workflow(
    id="research-workflow",
    name="Research Discovery Pipeline",
    description=(
        "Iterative research pipeline: Idea → Method → Experiment, "
        "driven by an Execution Manager that refines the goal each iteration."
    ),
    db=get_postgres_db(),
    steps=[
        Loop(
            name="Research Iteration Loop",
            steps=[
                idea_phase,
                method_phase,
                experiment_phase,
                Step(
                    name="Manager Evaluation",
                    agent=execution_manager,
                    add_workflow_history=True,
                    num_history_runs=3,
                ),
            ],
            end_condition=check_satisfied,
            max_iterations=3,
            forward_iteration_output=True,
        ),
    ],
)


# ---------------------------------------------------------------------------
# Entry point (for direct execution / testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    research_workflow.print_response(
        "Research the technical feasibility of using local LLMs for real-time "
        "financial signal generation in a low-latency trading environment.",
        markdown=True,
    )
```

---

## 13. Integration Notes

### `__init__.py` exports (if needed)

```python
# workflows/__init__.py
from workflows.research_workflow import research_workflow
```

### Adding to `task_team`

To allow on-demand invocation from the interactive team, add the workflow as a tool
(see `agno` docs: *Execute Workflow from an Agent*):

```python
# In teams/task_team.py — add workflow tool
from agno.tools.workflow import WorkflowTool
from workflows.research_workflow import research_workflow

# Add to task_team's tools:
tools=[WorkflowTool(workflow=research_workflow)]
```

---

## 14. Key Design Decisions

| Decision | Rationale |
|---|---|
| `planning_team` and `control_team` shared across all 3 phases | Single definition, phase context injected via input message |
| `execution_manager` uses `add_workflow_history=True` | Manager effectively evaluates the accumulated output of *all* phases. |
| `forward_iteration_output=True` on `Loop` | Passes ONLY the final output of the Loop (the Manager's refined_goal) back as the starting input for the next cycle's Idea Plan. |
| `idea_hater` always invoked after `idea_maker` | Adversarial pairing enforced via `control_team` coordinator instructions |
| Sandboxed execution via DockerTools | `docker_executor` safely runs code generated by `engineer` inside ephemeral Docker containers without risking the host machine. |

---

## 15. Testing Checklist

- [ ] `planner` produces valid Markdown plan for each phase type
- [ ] `plan_reviewer` correctly returns `APPROVED` / `NEEDS_REVISION`
- [ ] `planning_team` terminates the debate loop within 3 rounds
- [ ] `idea_maker` + `idea_hater` are always invoked as a pair by `control_team`
- [ ] `researcher` uses multiple EXA queries, not a single broad one
- [ ] `execution_manager` returns valid `ManagerDecision` JSON
- [ ] `check_satisfied` correctly parses `ManagerDecision` and handles fallback
- [ ] Iteration 2 planning correctly references Iteration 1 experiment results
- [ ] `Loop` terminates at `max_iterations=3` even if `end_condition` never fires
