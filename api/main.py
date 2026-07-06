"""
Agent Society API
-----------------
FastAPI backend that exposes the Agent Society as a REST API.

Endpoints:
  POST /run       → Submit a task, get a full result (saved to database)
  GET  /status    → Check system health
  GET  /memory    → View shared memory state (debug)
  GET  /log       → View agent conversation log
  GET  /sessions  → List all past sessions from the database
  GET  /sessions/{id} → View a specific past session in full

Deploy this on Alibaba Cloud ECS or Function Compute.
(Required for hackathon: must show Alibaba Cloud deployment)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from orchestrator.orchestrator import AgentSocietyOrchestrator
from database.db import save_session, get_all_sessions, get_session

app = FastAPI(
    title="Agent Society API",
    description="Multi-agent collaboration system powered by Qwen Cloud",
    version="1.0.0",
)

# Allow the frontend (frontend/index.html) to talk to this API
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


class TaskResponse(BaseModel):
    session_id: int
    final_output: str
    plan: str
    research_summary: str
    rounds_completed: int
    efficiency_gain: str
    processing_time_seconds: float
    agent_log: list


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.get("/api")
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
    The result is also saved permanently to the SQLite database.
    """
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    start = time.time()

    try:
        orchestrator = AgentSocietyOrchestrator()
        result = orchestrator.run(request.task, max_rounds=request.max_rounds)
        elapsed = round(time.time() - start, 2)

        # Persist this run to the database
        session_id = save_session(
            task=request.task,
            plan=result["plan"],
            research=result["research_summary"],
            final_output=result["final_output"],
            rounds_completed=result["rounds_completed"],
            efficiency_gain=result["efficiency_gain"],
            conversation_log=result["conversation_log"],
        )

        return TaskResponse(
            session_id=session_id,
            final_output=result["final_output"],
            plan=result["plan"],
            research_summary=result["research_summary"],
            rounds_completed=result["rounds_completed"],
            efficiency_gain=result["efficiency_gain"],
            processing_time_seconds=elapsed,
            agent_log=result["conversation_log"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def list_sessions():
    """Returns every past session saved in the database, most recent first."""
    sessions = get_all_sessions()
    return {"count": len(sessions), "sessions": sessions}


@app.get("/sessions/{session_id}")
async def get_session_detail(session_id: int):
    """Returns the full detail of one past session."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


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


# ── SERVE THE FRONTEND ────────────────────────────────────────────────────────
# This mounts frontend/index.html to be served directly at http://localhost:8000/
# No separate server needed — one port (8000) serves both the API and the UI.
# IMPORTANT: this must be the LAST route registered, so it doesn't override
# the API routes above (FastAPI checks explicit routes before this catch-all).
_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")


# ── STARTUP ───────────────────────────────────────────────────────────────────
# Run with: uvicorn api.main:app --reload --port 8000

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
