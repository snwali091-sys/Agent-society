# 🤖 Agent Society
### Track 3 Entry — Global AI Hackathon with Qwen Cloud

A multi-agent collaboration system where **5 specialized AI agents** work together through task division, dialogue, and negotiation to accomplish complex tasks — measurably outperforming single-agent baselines.

---

## What It Does

Give Agent Society any complex task. It automatically:

1. **Plans** — A Planner agent decomposes the task into subtasks and assigns roles
2. **Researches** — A Researcher agent synthesizes relevant knowledge
3. **Writes** — A Writer agent produces a first draft using the plan and research
4. **Critiques** — A Critic agent scores the draft and provides specific feedback
5. **Refines** — Writer incorporates feedback and improves (up to N rounds)
6. **Delivers** — An Executor packages the polished final result

All agents share a **common memory whiteboard** and can speak directly to each other. Every session is persisted to a **SQLite database**, viewable through the web interface or `view_sessions.py`.

### New — Refine Without Restarting
After receiving a result, you can ask the system to adjust it — "make it shorter," "add more detail on risk mitigation" — and the Writer and Critic revise the **existing output directly**, without re-running the Planner or Researcher from scratch. This keeps follow-up requests focused on the same piece of work instead of wandering into unrelated territory.

### New — Copy, Download, and Session History
Every result can be **copied to clipboard** or **downloaded as a Markdown file** with one click. All tasks run during a session appear in a **Previous Tasks** list — click any entry to instantly bring that result back on screen without re-running anything.

---

## Architecture

```
User (Web UI or CLI)
    │
    ▼
┌─────────────┐
│ ORCHESTRATOR │  ← Master coordinator, routes tasks, manages state
└──────┬──────┘
       │
   ┌───┴──────────────────────────────────────┐
   │            SHARED MEMORY                 │
   │  (plan, research, drafts, critiques)     │
   └───┬───────┬────────┬────────┬────────────┘
       │       │        │        │
  ┌────▼──┐ ┌──▼────┐ ┌─▼─────┐ ┌▼───────┐ ┌─────────┐
  │PLANNER│ │RESRCH │ │WRITER │ │CRITIC │ │EXECUTOR │
  │(fast) │ │       │ │       │ │(fast) │ │         │
  └───────┘ └───────┘ └───────┘ └───────┘ └─────────┘
       │                  ▲           │
       │                  └───────────┘
       │             Critic ↔ Writer negotiation loop
       ▼
  Qwen Cloud (DashScope API, international endpoint)
       │
       ▼
  SQLite Database (sessions.db) — persists every run
       │
       ▼
  Final Output + Audit Log + Efficiency Metrics
       │
       ▼
  Web Frontend — served directly by FastAPI at http://localhost:8000
```

Planner and Critic use `qwen-turbo` (faster, tuned for structured output); Writer, Researcher, and Executor use `qwen-plus` (deeper generation quality). This split was made specifically to reduce total response time without sacrificing output quality.

**Full visual diagram:** `architecture_diagram_v2.jpg`

---

## Quick Start

### 1. Clone and enter the project
```bash
git clone https://github.com/snwali091-sys/Agent-society.git
cd Agent-society
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
```bash
cp .env.example .env
```
Edit `.env` and add your key from **home.qwencloud.com**:
```
DASHSCOPE_API_KEY=sk-your-real-key-here
```

### 4. Launch the application

**Option A — One-click desktop launch (Windows):**
Run once to create a desktop icon:
```powershell
powershell -ExecutionPolicy Bypass -File Create_Desktop_Shortcut.ps1
```
Then double-click **Agent Society** on your Desktop any time.

**Option B — Manual (works on any platform, shows live logs):**
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```
Then open `http://localhost:8000` in your browser.

**Option C — Command line only, no browser:**
```bash
python main.py --task "Write a go-to-market strategy for an AI tutoring app in Nigeria"
```

---

## Using the Web Interface

1. Type a task and click **Run Agent Society**
2. Watch the live status while all five agents work
3. Once complete, use the **Refine** box to request adjustments to the same result
4. Use **Copy** or **Download** to save the output
5. Every task appears in the **Previous tasks** history — click any entry to bring it back

---

## Command Line Usage

```bash
python main.py --demo                          # Run a preset demo task
python main.py --task "Your task here"          # Run your own task
python main.py --benchmark                      # Compare vs single-agent baseline
python view_sessions.py                         # View all saved sessions
python view_sessions.py --id 3                   # View one session in full detail
```

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the web frontend |
| `/api` | GET | System info (JSON) |
| `/status` | GET | Health check |
| `/run` | POST | Submit a new task |
| `/refine` | POST | Refine an existing result |
| `/sessions` | GET | List all saved sessions |
| `/sessions/{id}` | GET | View one session in full |
| `/demo` | GET | Run a preset demo task |
| `/docs` | GET | Interactive API documentation (Swagger UI) |

---

## Verified Setup Notes

| Issue | Resolution Already Applied |
|-------|----------------------------|
| `ModuleNotFoundError` | `__init__.py` present in every module folder |
| `401 AuthenticationError` | International DashScope endpoint set correctly in `orchestrator.py` |
| API key not loading | `load_dotenv()` called before any API client is created |
| Slow response times | Planner/Critic use `qwen-turbo`; token budgets reduced for structured agents; default rounds lowered |
| Markdown showing raw `**`/`##` | Custom renderer processes lists before bold/italic; safety net strips any leftover stray markers |

Always run all commands from the **repository root** — the folder containing `main.py`.

---

## Alibaba Cloud Deployment

- **Qwen Cloud (DashScope)** — All 5 agents call the international endpoint
- **Alibaba Cloud ECS** — Backend deployment target (Ubuntu 22.04, Singapore region)
- **Alibaba Cloud OSS** — Session log mirroring for durability
- Full deployment code and instructions: `alibaba_cloud_deploy.py`

---

## Hackathon Criteria — How We Score

| Criterion | Implementation |
|-----------|----------------|
| **Innovation & AI Creativity (30%)** | Custom Critic-Writer negotiation loop; refine-without-restart capability; per-agent model tuning for speed |
| **Technical Depth (30%)** | Modular architecture; SQLite persistence; REST API; configurable rounds; full audit trail |
| **Problem Value & Impact (25%)** | `benchmark.py` proves measurable quality gain over single-agent baseline |
| **Presentation & Documentation (15%)** | Architecture diagram, this README, live web demo, video walkthrough |

---

## Project Structure

```
agent_society/
├── agents/              # Five specialist agents
├── api/                 # FastAPI backend (serves frontend + REST API)
├── database/             # SQLite persistence layer
├── frontend/             # Web interface
├── memory/               # Shared whiteboard
├── orchestrator/          # Master coordinator + refine logic
├── main.py                # CLI entry point
├── simulate.py             # Offline demo (no API key needed)
├── benchmark.py             # Efficiency comparison tool
├── view_sessions.py          # Database session viewer
├── alibaba_cloud_deploy.py    # Cloud deployment code
├── Create_Desktop_Shortcut.ps1 # One-click launcher setup
├── Launch_Silent.ps1            # Background launch logic
├── Start_Manually.bat            # Visible fallback launcher
└── architecture_diagram_v2.jpg    # Full system diagram
```

---

## License

MIT License — see `LICENSE` file.
