"""
Writer Agent
------------
The PRODUCER of the society.

What it does:
  - Reads the plan + research from shared memory
  - Generates the core content/output
  - Incorporates critic feedback in subsequent rounds
  - Improves iteratively — never defensive about changes

This is the agent doing the actual "work" output.
In a business context this could be: writing a report, generating code,
composing an email, building a data pipeline, etc.
"""

from agents.base_agent import BaseAgent

WRITER_ROLE = """
You are the Content Writer in an Agent Society.
Your job: produce high-quality, structured output based on the plan and research provided.

Guidelines:
- Follow the plan's structure closely
- Incorporate all research data naturally
- Write clearly for the target audience
- Use headings, bullet points, and sections where appropriate
- When revising based on critic feedback, explicitly address each critique point

If given a previous draft + critique, you MUST:
1. Acknowledge each criticism
2. Show specifically how you fixed it
3. Deliver the improved version
"""


class WriterAgent(BaseAgent):
    def __init__(self, client, model, memory):
        super().__init__(
            client=client,
            model=model,
            memory=memory,
            name="writer",
            role_prompt=WRITER_ROLE,
        )

    def run(self, prompt: str) -> str:
        round_num = self.memory.get("write_round") or 0
        round_num += 1
        self.memory.set("write_round", round_num)
        print(f"   ✍️  Writer composing (iteration {round_num})...")
        draft = super().run(prompt)
        self.memory.set(f"draft_v{round_num}", draft)
        return draft
