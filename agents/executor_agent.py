"""
Executor Agent
--------------
The DELIVERY SPECIALIST of the society.

What it does:
  - Takes the approved final draft
  - Formats it professionally for delivery
  - Adds metadata, summaries, and action items
  - Packages the complete result bundle

This is the "last mile" agent — turns internal work into
something the end user actually receives.

It also validates all deliverables meet submission requirements
(important for hackathon compliance).
"""

from agents.base_agent import BaseAgent

EXECUTOR_ROLE = """
You are the Final Executor in an Agent Society.
Your job: polish, format, and package the final deliverable.

You MUST:
1. Start with a concise EXECUTIVE SUMMARY (3-5 sentences)
2. Present the full, structured content
3. End with ACTION ITEMS (concrete next steps)
4. Add a METADATA section:
   - Task type
   - Agents involved
   - Quality score
   - Confidence level

Make the output feel professional, complete, and ready for real use.
Never just copy the draft — genuinely improve its presentation.
"""


class ExecutorAgent(BaseAgent):
    def __init__(self, client, model, memory):
        super().__init__(
            client=client,
            model=model,
            memory=memory,
            name="executor",
            role_prompt=EXECUTOR_ROLE,
        )

    def run(self, prompt: str) -> str:
        print(f"   📦 Executor packaging final deliverable...")
        final = super().run(prompt)
        self.memory.set("final_deliverable", final)
        return final
