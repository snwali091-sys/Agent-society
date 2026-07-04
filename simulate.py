"""
Agent Society — OFFLINE SIMULATOR
===================================
Runs the full 5-agent pipeline WITHOUT a real Qwen Cloud API key.
All agent responses are simulated so you can see the exact flow,
shared memory updates, dialogue logs, and efficiency metrics.

Run with:
    python simulate.py
    python simulate.py --task "Your own task here"
"""

import argparse
import time
import json
import random
from datetime import datetime


# ─── COLOUR OUTPUT FOR THE TERMINAL ──────────────────────────────────────────
# Makes the simulation easy to follow at a glance

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
PURPLE = "\033[95m"
BLUE   = "\033[94m"
GREY   = "\033[90m"
WHITE  = "\033[97m"

def c(text, colour): return f"{colour}{text}{RESET}"

def banner(text, colour=CYAN):
    print("\n" + colour + "━" * 60 + RESET)
    print(colour + BOLD + f"  {text}" + RESET)
    print(colour + "━" * 60 + RESET)

def agent_print(agent, message, colour=WHITE):
    tag = c(f"[{agent.upper():^12}]", colour)
    print(f"{tag} {message}")

def memory_print(key, preview):
    print(c(f"  💾 MEMORY['{key}'] = {preview[:70]}...", GREY))

def pause(secs=0.4):
    time.sleep(secs)


# ─── SHARED MEMORY ────────────────────────────────────────────────────────────

class SharedMemory:
    """The whiteboard all agents read from and write to."""

    def __init__(self):
        self._store = {}
        self._log   = []

    def set(self, key, value):
        self._store[key] = value
        self._log.append({"action": "WRITE", "key": key, "by": "agent"})
        memory_print(key, str(value))

    def get(self, key, default=None):
        return self._store.get(key, default)

    def all_keys(self):
        return list(self._store.keys())

    def export(self, path="memory_snapshot.json"):
        with open(path, "w") as f:
            json.dump({k: str(v)[:200] for k, v in self._store.items()}, f, indent=2)
        return path


# ─── MOCK AGENT RESPONSES ────────────────────────────────────────────────────
# These simulate what Qwen Cloud would actually return.
# Structured to look realistic for the hackathon demo.

def mock_plan(task):
    return f"""TASK BREAKDOWN:
1. [RESEARCHER] - Research key facts, market data, and background for: {task}
2. [WRITER]     - Draft a comprehensive structured response using research findings
3. [CRITIC]     - Evaluate draft on accuracy, completeness, clarity, structure, depth
4. [WRITER]     - Revise draft based on critique feedback (if needed)
5. [EXECUTOR]   - Package final approved output with executive summary and action items

DEPENDENCIES:
- Step 2 requires completion of Step 1 (Writer needs research data)
- Step 3 requires completion of Step 2 (Critic needs draft to review)
- Step 4 requires completion of Step 3 (Writer needs critique to improve)
- Step 5 requires APPROVED status from Critic

SUCCESS CRITERIA:
- Critic overall score >= 8/10
- All sections of the task addressed
- Clear actionable output delivered to user"""


def mock_research(task):
    return f"""KEY FACTS:
- {task[:50]} is a growing area with significant market opportunity
- Key players include established enterprises and fast-moving startups
- Adoption is accelerating driven by productivity and cost reduction needs
- Regulatory considerations vary by region and industry vertical

DATA POINTS:
- Market growing at estimated 25-35% CAGR year-over-year
- Early adopters reporting 30-50% efficiency improvements
- Investment in this space exceeded $12B globally in the past 12 months
- Top 3 use cases: automation, decision support, content generation

KNOWLEDGE GAPS:
- Long-term sustainability of current growth rates unclear
- Standardisation across tools and platforms still maturing
- Talent availability remains a bottleneck for large-scale adoption

RECOMMENDED FOCUS AREAS:
- Lead with concrete ROI and efficiency data
- Address risk and mitigation strategies
- Include comparison to alternatives for credibility"""


def mock_draft(task, research, critique=None, round_num=1):
    if round_num == 1:
        return f"""# Analysis: {task}

## Executive Overview
This analysis examines {task}, covering key market dynamics,
strategic considerations, and actionable recommendations.

## Market Context
Based on current research, this domain is experiencing substantial growth,
with adoption rates accelerating across enterprise and SMB segments alike.
Key drivers include cost pressure, talent scarcity, and competitive differentiation.

## Key Findings
1. **Market Opportunity**: Significant headroom remains despite early adoption by leaders
2. **Competitive Landscape**: Fragmented market with no single dominant player
3. **Implementation Considerations**: Integration complexity is the primary barrier
4. **ROI Profile**: Payback periods of 6-18 months typical for well-scoped projects

## Risks & Mitigations
- Technology risk → mitigated by vendor due diligence and pilot programs
- Change management risk → mitigated by phased rollout and training investment
- Regulatory risk → mitigated by legal review and compliance monitoring

## Recommendations
1. Begin with a focused pilot in highest-impact area
2. Establish clear KPIs before launch
3. Build internal capability alongside vendor partnerships

*Note: Section 3 could benefit from more specific market statistics.*"""
    else:
        return f"""# Analysis: {task}
*(Revised — addressing all critique points)*

## Executive Overview
This analysis examines {task} with rigorous data-backed insights,
addressing market size, competitive dynamics, and strategic recommendations.

## Market Context
The global market is valued at approximately $45B and growing at 28% CAGR.
Research confirms adoption is accelerating with 73% of enterprises planning
increased investment in the next 18 months (Source: industry consensus data).

## Key Findings
1. **Market Opportunity**: $45B market, 28% CAGR, concentrated in North America (42%) and Asia-Pacific (31%)
2. **Competitive Landscape**: Top 5 vendors hold 38% share; remaining 62% fragmented among 200+ players
3. **Implementation**: Average deployment time 3-6 months; integration with legacy systems is primary barrier (cited by 67% of enterprises)
4. **ROI Profile**: Median payback 14 months; leaders achieving 3.2x ROI over 3 years

## Risks & Mitigations
- Technology risk → mitigated by vendor due diligence, SLA requirements, and pilot programs
- Change management risk → mitigated by phased rollout, executive sponsorship, and training
- Regulatory risk → mitigated by legal review, data governance frameworks, and compliance monitoring
- Vendor lock-in risk → mitigated by API-first architecture and open standards adoption

## Recommendations
1. **Immediate (0-3 months)**: Define success metrics and run a constrained pilot
2. **Short-term (3-9 months)**: Scale pilot to 2-3 business units based on results
3. **Medium-term (9-18 months)**: Full deployment with continuous optimisation loop

## Conclusion
The evidence strongly supports strategic investment. First-mover advantage
is meaningful; organisations that act in the next 12 months position themselves
ahead of what will be a more competitive landscape by 2026."""


def mock_critique(draft, round_num=1):
    if round_num == 1:
        return """SCORES:
- Accuracy:     7/10  ← Good but missing specific data points
- Completeness: 6/10  ← Section 3 too thin; risks section needs expansion
- Clarity:      8/10  ← Well written and easy to follow
- Structure:    8/10  ← Logical flow, good headings
- Depth:        6/10  ← Surface-level on market sizing; no citations
- OVERALL:      7/10

SPECIFIC ISSUES:
1. [Section: Market Context] Claims growth is "substantial" — add specific % and market size in $
2. [Section: Key Findings #3] "Integration complexity" asserted without supporting evidence
3. [Section: Risks] Technology risk mitigation is vague — what specific due diligence steps?
4. [Missing] No timeline or phased approach in recommendations
5. [Missing] No competitive comparison — reader cannot benchmark against alternatives

VERDICT: NEEDS REVISION
Priority fixes: Add market statistics, expand risks, add timeline to recommendations."""
    else:
        return """SCORES:
- Accuracy:     9/10  ← Specific data now present ($45B, 28% CAGR, 73% adoption intent)
- Completeness: 9/10  ← All sections now fully developed with supporting evidence
- Clarity:      9/10  ← Excellent readability, concrete examples throughout
- Structure:    9/10  ← Timeline in recommendations greatly improves actionability
- Depth:        8/10  ← Strong improvement; minor: could add one more competitive reference
- OVERALL:      8.8/10

All previous critique points addressed:
✓ Market size and growth rate now specified
✓ Integration complexity supported with 67% statistic
✓ Risk mitigations now concrete and specific
✓ Recommendations include 3-phase timeline
✓ Market share data adds competitive context

VERDICT: APPROVED ✅
This is publication-ready. The phased recommendations are particularly strong."""


def mock_final(draft, task):
    return f"""
╔══════════════════════════════════════════════════════════╗
║              AGENT SOCIETY — FINAL DELIVERABLE           ║
╚══════════════════════════════════════════════════════════╝

EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━
This deliverable provides a comprehensive, data-backed analysis of "{task}".
Five specialist agents collaborated across 2 rounds of research, drafting,
and critique to produce a quality-assured output (score: 8.8/10).
The findings support strategic investment with clear ROI evidence and
a phased implementation roadmap.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FULL CONTENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{draft}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTION ITEMS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Schedule stakeholder review of this analysis within 5 business days
2. Define pilot scope and success metrics (target: end of current quarter)
3. Issue RFP to top 3 vendors for comparative evaluation
4. Appoint internal project champion with executive sponsorship
5. Set 90-day checkpoint to review pilot KPIs and go/no-go for full deployment

METADATA
━━━━━━━━━
Task type       : Strategic analysis
Agents involved : Planner, Researcher, Writer (×2), Critic (×2), Executor
Quality score   : 8.8 / 10
Rounds required : 2 of 3 maximum
Confidence      : High"""


# ─── SINGLE-AGENT BASELINE (for benchmark comparison) ────────────────────────

def single_agent_baseline(task):
    return f"""Here is an analysis of {task}:

This is an important and growing area. There are many considerations
to keep in mind including market dynamics, competitive forces, and
implementation challenges.

Key points:
- The market is growing
- There are risks to consider
- Recommendations depend on your specific situation

In conclusion, careful evaluation is recommended before proceeding."""


# ─── MAIN SIMULATION ─────────────────────────────────────────────────────────

def run_simulation(task: str):
    memory = SharedMemory()
    conversation_log = []
    start_time = time.time()

    banner("AGENT SOCIETY — LIVE SIMULATION", CYAN)
    print(c(f"\n  Task: ", GREY) + c(f'"{task}"', WHITE))
    print(c(f"  Started: {datetime.now().strftime('%H:%M:%S')}", GREY))
    print(c(f"  Mode: OFFLINE SIMULATION (no API key needed)\n", YELLOW))

    # ── PHASE 1: PLANNER ─────────────────────────────────────────────────────
    banner("PHASE 1 — PLANNER AGENT", BLUE)
    agent_print("PLANNER", "Receiving task from orchestrator...", BLUE)
    pause(0.5)
    agent_print("PLANNER", "Decomposing into subtasks and assigning roles...", BLUE)
    pause(0.8)

    plan = mock_plan(task)
    memory.set("original_task", task)
    memory.set("plan", plan)
    conversation_log.append({"from": "planner", "to": "orchestrator", "msg": "Plan ready"})

    print(c("\n  📋 PLAN OUTPUT:", BLUE))
    for line in plan.split("\n"):
        print(c(f"     {line}", WHITE))
    pause(0.5)
    agent_print("PLANNER", c("✓ Plan stored in shared memory", GREEN), BLUE)

    # ── PHASE 2: RESEARCHER ───────────────────────────────────────────────────
    banner("PHASE 2 — RESEARCHER AGENT", GREEN)
    agent_print("RESEARCHER", "Reading plan from shared memory...", GREEN)
    pause(0.4)
    agent_print("RESEARCHER", "Synthesising knowledge base...", GREEN)
    pause(0.8)

    research = mock_research(task)
    memory.set("research", research)
    conversation_log.append({"from": "researcher", "to": "orchestrator", "msg": "Research complete"})

    print(c("\n  🔍 RESEARCH OUTPUT:", GREEN))
    for line in research.split("\n")[:10]:
        print(c(f"     {line}", WHITE))
    print(c("     ... (truncated for display)", GREY))
    pause(0.4)
    agent_print("RESEARCHER", c("✓ Research stored in shared memory", GREEN), GREEN)

    # ── PHASE 3: WRITER + CRITIC LOOP ────────────────────────────────────────
    final_draft = None
    final_critique = None

    for round_num in range(1, 4):
        banner(f"PHASE 3 — WRITER × CRITIC LOOP  (Round {round_num}/3)", YELLOW)

        # Writer
        agent_print("WRITER", f"Reading plan + research from shared memory...", YELLOW)
        pause(0.4)
        if round_num > 1:
            agent_print("WRITER", c(f"Also reading critique from round {round_num-1}...", GREY), YELLOW)
            pause(0.3)
        agent_print("WRITER", f"Composing draft (iteration {round_num})...", YELLOW)
        pause(0.9)

        draft = mock_draft(task, research, critique=final_critique, round_num=round_num)
        memory.set(f"draft_v{round_num}", draft)
        memory.set("current_draft", draft)
        conversation_log.append({"from": "writer", "to": "critic", "msg": f"Draft v{round_num} ready for review"})

        agent_print("WRITER", c(f"✓ Draft v{round_num} produced ({len(draft.split())} words)", GREEN), YELLOW)
        print(c(f"\n  ✍️  DRAFT v{round_num} PREVIEW (first 3 lines):", YELLOW))
        for line in draft.split("\n")[:3]:
            print(c(f"     {line}", WHITE))
        print(c("     ...", GREY))

        pause(0.5)

        # Critic
        print()
        agent_print("CRITIC", f"Reading draft v{round_num} from shared memory...", RED)
        pause(0.4)
        agent_print("CRITIC", "Evaluating: accuracy, completeness, clarity, structure, depth...", RED)
        pause(0.9)

        critique = mock_critique(draft, round_num)
        memory.set("critique", critique)
        memory.set("revision_count", round_num)
        conversation_log.append({"from": "critic", "to": "writer", "msg": critique[:100]})

        print(c(f"\n  🔎 CRITIQUE (Round {round_num}):", RED))
        for line in critique.split("\n"):
            colour = GREEN if "APPROVED" in line else (RED if "NEEDS REVISION" in line else WHITE)
            print(c(f"     {line}", colour))

        final_draft   = draft
        final_critique = critique

        if "APPROVED" in critique:
            agent_print("CRITIC", c(f"✅ APPROVED in round {round_num}! Stopping loop early.", GREEN), RED)
            pause(0.5)
            break
        else:
            agent_print("CRITIC", c(f"⚠️  NEEDS REVISION — sending feedback to Writer", YELLOW), RED)
            pause(0.5)

    # ── PHASE 4: EXECUTOR ─────────────────────────────────────────────────────
    banner("PHASE 4 — EXECUTOR AGENT", PURPLE)
    agent_print("EXECUTOR", "Reading approved final draft from shared memory...", PURPLE)
    pause(0.4)
    agent_print("EXECUTOR", "Packaging: executive summary + action items + metadata...", PURPLE)
    pause(0.8)

    final_output = mock_final(final_draft, task)
    memory.set("final_deliverable", final_output)
    conversation_log.append({"from": "executor", "to": "user", "msg": "Final deliverable ready"})

    agent_print("EXECUTOR", c("✓ Final output packaged and ready", GREEN), PURPLE)

    # ── RESULTS ───────────────────────────────────────────────────────────────
    elapsed = round(time.time() - start_time, 1)

    banner("SIMULATION COMPLETE — RESULTS", CYAN)
    print(c(f"\n  ⏱️  Total time      : {elapsed}s", WHITE))
    print(c(f"  🔄  Rounds          : {round_num} of 3 maximum", WHITE))
    print(c(f"  🤖  Agents used     : 5 (Planner, Researcher, Writer, Critic, Executor)", WHITE))
    print(c(f"  💾  Memory keys set : {len(memory.all_keys())}", WHITE))
    print(c(f"  💬  Agent messages  : {len(conversation_log)}", WHITE))

    # Benchmark comparison
    baseline = single_agent_baseline(task)
    multi_words = len(final_draft.split())
    single_words = len(baseline.split())
    quality_gain = "+35% est."

    print(c(f"\n  📊 EFFICIENCY BENCHMARK:", CYAN))
    print(c(f"     Single agent output   : {single_words} words — generic, no data", RED))
    print(c(f"     Agent Society output  : {multi_words} words — structured, data-backed", GREEN))
    print(c(f"     Estimated quality gain: {quality_gain}", GREEN))

    print(c(f"\n  🗝️  SHARED MEMORY KEYS WRITTEN:", GREY))
    for key in memory.all_keys():
        print(c(f"     • {key}", GREY))

    print(c(f"\n  💬 AGENT CONVERSATION LOG:", GREY))
    for entry in conversation_log:
        print(c(f"     {entry['from'].upper()} → {entry['to'].upper()}: {entry['msg'][:60]}...", GREY))

    # Save outputs
    snapshot_path = memory.export("memory_snapshot.json")

    with open("final_output.txt", "w", encoding="utf-8", errors="replace") as f:
        f.write(final_output)

    with open("conversation_log.json", "w") as f:
        json.dump(conversation_log, f, indent=2)

    print(c(f"\n  📁 FILES SAVED:", GREEN))
    print(c(f"     • memory_snapshot.json    ← shared memory state", WHITE))
    print(c(f"     • final_output.txt        ← the deliverable", WHITE))
    print(c(f"     • conversation_log.json   ← full agent dialogue", WHITE))

    banner("FINAL DELIVERABLE PREVIEW", GREEN)
    print(final_output[:1200])
    print(c("\n  ... (full output in final_output.txt)", GREY))

    print(c("\n✅ Simulation complete. This is exactly what runs with a real Qwen API key.\n", GREEN))


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent Society Offline Simulator")
    parser.add_argument("--task", type=str, default=None, help="Task to simulate")
    args = parser.parse_args()

    default_task = (
        "Write a competitive market analysis for AI-powered customer service tools "
        "targeting mid-size e-commerce businesses in West Africa"
    )

    task = args.task or default_task
    run_simulation(task)
