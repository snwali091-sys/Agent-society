"""
Critic Agent
------------
The QUALITY CONTROLLER of the society.

What it does:
  - Reviews every Writer draft against the original task
  - Scores quality from 1–10 across multiple dimensions
  - Provides specific, actionable improvement feedback
  - Says "APPROVED" only when the output genuinely meets the bar

This is how the society self-corrects without human intervention.
The Critic-Writer loop is the core quality mechanism.

Real-world analogy: code review, editorial review, peer review.
"""

from agents.base_agent import BaseAgent

CRITIC_ROLE = """
You are the Quality Critic in an Agent Society.
Your job: rigorously evaluate drafts and provide clear improvement feedback.

Evaluation dimensions:
1. ACCURACY     - Is every claim correct and supported?
2. COMPLETENESS - Does it fully address the task?
3. CLARITY      - Is it easy to understand?
4. STRUCTURE    - Is it well-organized?
5. DEPTH        - Does it go beyond surface level?

Output format:
SCORES:
- Accuracy:     X/10
- Completeness: X/10
- Clarity:      X/10
- Structure:    X/10
- Depth:        X/10
- OVERALL:      X/10

SPECIFIC ISSUES:
1. [Section X] Issue description → How to fix it
2. ...

VERDICT: [APPROVED if overall >= 8] or [NEEDS REVISION]

Be honest and specific. Vague feedback wastes cycles.
"""


class CriticAgent(BaseAgent):
    def __init__(self, client, model, memory):
        super().__init__(
            client=client,
            model=model,
            memory=memory,
            name="critic",
            role_prompt=CRITIC_ROLE,
            max_tokens=800,   # Scores and short critique notes — no need for 3000
        )

    def run(self, prompt: str) -> str:
        print(f"   🔎 Critic evaluating quality...")
        critique = super().run(prompt)
        
        # Track how many revision cycles we've gone through
        revisions = self.memory.get("revision_count") or 0
        self.memory.set("revision_count", revisions + 1)
        self.memory.set("latest_critique", critique)
        return critique

    def negotiate(self, writer_agent, disagreement: str) -> str:
        """
        When the Writer disagrees with critique, they negotiate.
        This models real team dynamics where agents resolve conflicts
        through structured dialogue rather than one winning arbitrarily.
        """
        print(f"   ⚡ Negotiation: Critic ↔ Writer...")
        writer_response = writer_agent.run(
            f"The Critic says: {disagreement}\nDo you agree? Provide counter-arguments if not."
        )
        # Critic considers the writer's counter-argument
        return self.run(
            f"Writer's counter-argument: {writer_response}\n"
            "Update your critique considering this new perspective."
        )
