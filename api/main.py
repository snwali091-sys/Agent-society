"""
Agent Society API
-----------------
FastAPI backend that exposes the Agent Society as a REST API.

Endpoints:
  POST /run     → Submit a task, get a full result
  GET  /status  → Check system health
  GET  /memory  → View shared memory state (debug)
  GET  /log     → View agent conversation log

Deploy this on Alibaba Cloud ECS or Function Compute.
(Required for hackathon: must show Alibaba Cloud deployment)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from orchestrator.orchestrator import AgentSocietyOrchestrator

app = FastAPI(
    title="Agent Society API",
    description="Multi-agent collaboration system powered by Qwen Cloud",
    version="1.0.0",
)

# Allow frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REQUEST / RESPONSE MODELS ─────────────────────────────────────────────────

class TaskRequest(BaseModel):
    task: str                   # The user's task description
    max_rounds: int = 3         # How many critique-refine cycles to run
    # Example: {"task": "Analyse the market opportunity for AI healthcare tools"}


class TaskResponse(BaseModel):
    final_output: str
    plan: str
    research_summary: str
    rounds_completed: int
    efficiency_gain: str
    processing_time_seconds: float
    agent_log: list


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "Agent Society",
        "status": "online",
        "tracks": ["Track 3: Agent Society"],
        "agents": ["planner", "researcher", "writer", "critic", "executor"],
    }


@app.get("/status")
def health_check():
    """Judges can hit this to verify the service is live."""
    return {"status": "healthy", "timestamp": time.time()}


@app.post("/run", response_model=TaskResponse)
async def run_task(request: TaskRequest):
    """
    Main endpoint. Submit a task, get a complete multi-agent result.
    
    The orchestrator spins up all agents, runs the Plan→Research→Write→Critique
    loop, and returns the final polished output.
    """
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    start = time.time()

    try:
        # Each request creates a fresh orchestrator (fresh shared memory)
        orchestrator = AgentSocietyOrchestrator()
        result = orchestrator.run(request.task, max_rounds=request.max_rounds)

        return TaskResponse(
            final_output=result["final_output"],
            plan=result["plan"],
            research_summary=result["research_summary"],
            rounds_completed=result["rounds_completed"],
            efficiency_gain=result["efficiency_gain"],
            processing_time_seconds=round(time.time() - start, 2),
            agent_log=result["conversation_log"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/demo")
async def demo():
    """
    Runs a pre-baked demo task.
    Perfect for live hackathon judges to quickly see the system in action.
    """
    orchestrator = AgentSocietyOrchestrator()
    result = orchestrator.run(
        "Create a comprehensive business plan for a sustainable fashion startup targeting Gen Z.",
        max_rounds=2,
    )
    return result


# ── STARTUP ───────────────────────────────────────────────────────────────────
# Run with: uvicorn api.main:app --reload --port 8000

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
