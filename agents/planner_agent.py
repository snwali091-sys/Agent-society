"""
Planner Agent
-------------
The STRATEGIST of the society.

What it does:
  - Takes a complex task from the user
  - Breaks it into clear, numbered subtasks
  - Assigns each subtask to the right specialist agent
  - Identifies dependencies (what must happen before what)

Why this matters:
  Without a planner, agents would guess what to do. With a planner,
  every agent knows their job, sequence, and success criteria.
"""

from agents.base_agent import BaseAgent

PLANNER_ROLE = """
You are the Strategic Planner in an Agent Society.
Your job is ONLY to plan — never to execute or write content directly.

When given a task, you MUST output a structured plan in this exact format:

TASK BREAKDOWN:
1. [RESEARCHER] - <what to research>
2. [WRITER]     - <what to draft>
3. [CRITIC]     - <what to evaluate>
4. [EXECUTOR]   - <how to finalize>

DEPENDENCIES:
- Step 2 requires completion of Step 1
- Step 3 requires completion of Step 2
(etc.)

SUCCESS CRITERIA:
- <clear, measurable definition of done>

Keep plans concise, specific, and actionable. 
Never include filler or vague instructions.
"""


class PlannerAgent(BaseAgent):
    def __init__(self, client, model, memory):
        super().__init__(
            client=client,
            model=model,
            memory=memory,
            name="planner",
            role_prompt=PLANNER_ROLE,
        )

    def run(self, prompt: str) -> str:
        print(f"   🗺️  Planner analyzing task complexity...")
        plan = super().run(prompt)
        
        # Store the structured plan so all agents can reference it
        self.memory.set("structured_plan", plan)
        return plan

    def reassign(self, failed_step: str, reason: str) -> str:
        """
        If an agent fails or produces poor output, the Planner can
        re-route that step to a different agent or adjust the approach.
        This is how the society handles failures gracefully.
        """
        return self.run(
            f"Step '{failed_step}' failed because: {reason}\n"
            "Please revise the plan to address this failure."
        )
