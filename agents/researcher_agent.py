"""
Researcher Agent
----------------
The ANALYST of the society.

What it does:
  - Reads the plan from shared memory
  - Synthesizes background knowledge relevant to the task
  - Identifies gaps or ambiguities the Writer should be aware of
  - Provides structured data/facts in a clean format

Think of it as the team member who goes to the library
(or internet) so the Writer doesn't have to.
"""

from agents.base_agent import BaseAgent

RESEARCHER_ROLE = """
You are the Research Specialist in an Agent Society.
Your job: gather, synthesize, and structure information relevant to the given task.

Output format:
KEY FACTS:
- <concise fact 1>
- <concise fact 2>
...

DATA POINTS:
- <statistics or specifics if applicable>

KNOWLEDGE GAPS:
- <what we don't know that might matter>

RECOMMENDED FOCUS AREAS:
- <what the writer should emphasize>

Be accurate, concise, and evidence-focused. Avoid opinions.
"""


class ResearcherAgent(BaseAgent):
    def __init__(self, client, model, memory):
        super().__init__(
            client=client,
            model=model,
            memory=memory,
            name="researcher",
            role_prompt=RESEARCHER_ROLE,
        )

    def run(self, prompt: str) -> str:
        print(f"   🔍 Researcher synthesizing knowledge base...")
        research = super().run(prompt)
        self.memory.set("research_data", research)
        return research
