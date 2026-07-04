"""
Base Agent
----------
Every agent in the society inherits from this class.
Think of it as the "employee contract" — defines what every agent CAN do.

Each agent has:
  - A NAME (who they are)
  - A ROLE (their job description, which shapes how Qwen responds)
  - A MEMORY (shared whiteboard all agents can read/write)
  - A run() method (execute their job on a given prompt)
"""

from memory.shared_memory import SharedMemory


class BaseAgent:
    def __init__(self, client, model: str, memory: SharedMemory, name: str, role_prompt: str):
        self.client = client
        self.model = model
        self.memory = memory
        self.name = name
        self.role_prompt = role_prompt   # This is the agent's "personality"

    def run(self, prompt: str) -> str:
        """
        Send a prompt to Qwen Cloud and return the response.
        
        The role_prompt is baked into the system message — this is HOW we
        give each agent a distinct personality and area of expertise.
        """
        # Build the context window: role + any relevant memory + the prompt
        context = self._build_context(prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.role_prompt},
                {"role": "user",   "content": context},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        result = response.choices[0].message.content

        # Store this agent's last output in shared memory under its own name
        self.memory.set(f"last_output_{self.name}", result)
        return result

    def _build_context(self, prompt: str) -> str:
        """
        Enriches the prompt with relevant shared memory.
        Agents can "read the board" before responding.
        """
        original_task = self.memory.get("original_task") or ""
        extra = f"[ORIGINAL TASK CONTEXT]\n{original_task}\n\n" if original_task else ""
        return extra + prompt

    def speak_to(self, other_agent: "BaseAgent", message: str) -> str:
        """
        Direct agent-to-agent communication.
        Agent A can ask Agent B a specific question.
        
        Example:
            critique = critic.speak_to(writer, "Is section 2 factually correct?")
        """
        return other_agent.run(f"Message from {self.name}: {message}")
