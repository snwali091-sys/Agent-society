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

All agents share a **common memory whiteboard** and can speak directly to each other. Every session is also persisted to a lightweight **SQLite database** so past runs can be reviewed later — see `database/` below.

---

## Architecture

```
User (CLI / API / minimal web UI)
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
  └───────┘ └───────┘ └───────┘ └───────┘ └─────────┘
       │                  ▲           │
       │                  └───────────┘
       │               Critic ↔ Writer loop
       ▼
  Qwen Cloud (DashScope API) → all 5 agents call this
       │
       ▼
  SQLite Database (sessions.db) → persists every run
       │
       ▼
  Final Output + Audit Log + Efficiency Metrics
       │
       ▼
  Minimal Web UI (frontend/index.html) → displays results
```

**All agents are powered by Qwen Cloud (DashScope API).**
**Backend deployed on Alibaba Cloud ECS.**
**Sessions persisted to SQLite locally, and optionally mirrored to Alibaba Cloud OSS.**

See `architecture_diagram.html` for the full visual diagram including the database and frontend layers.

---

## ⚠️ Verified Setup Steps (Tested End-to-End)

These are the **exact steps that were confirmed working**, including fixes for common issues.

### 1. Clone and enter the project
```bash
git clone https://github.com/snwali091-sys/Agent-society.git
cd Agent-society
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your `.env` file
Copy the template and fill in your real key:
```bash
cp .env.example .env
```
Open `.env` and add your Qwen Cloud key:
```
DASHSCOPE_API_KEY=sk-your-real-key-here
```

Get your key from **https://home.qwencloud.com/api-keys**

### 4. IMPORTANT — Confirm the correct API endpoint

Qwen Cloud (home.qwencloud.com) keys require the **international** DashScope endpoint, not the default one. This is already set correctly in `orchestrator/orchestrator.py` and `benchmark.py`:

```python
base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
```

> If you generated your key from a different Alibaba Cloud region, verify this matches your account's documentation before running.

### 5. Verify your key works
```bash
python test_key.py
```
Expected output:
```
Key found: 'sk-xxxxxxxxxxxxxxxxxxxxxxxx'
SUCCESS: Hello! How can I assist you today?
```

### 6. Run the offline simulator (no API key needed)
```bash
python simulate.py
```
This proves the full pipeline logic works before spending any API credits.

### 7. Run a real task
```bash
python main.py --demo
```
Or with your own task:
```bash
python main.py --task "Write a go-to-market strategy for an AI tutoring app in Nigeria"
```

### 8. Start the API backend
```bash
uvicorn api.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` for the interactive API explorer.

### 9. Open the minimal web frontend
Open `frontend/index.html` directly in your browser (after starting the API server in step 8). It submits tasks to your local API and displays the agent results.

### 10. View past sessions in the database
```bash
python view_sessions.py
```
This reads `database/sessions.db` and prints a history of every task run, its plan, final output, and quality score.

---

## Common Setup Issues (Already Fixed in This Repo)

| Issue | Fix Already Applied |
|---|---|
| `ModuleNotFoundError: No module named 'agents'` | `__init__.py` files included in `agents/`, `memory/`, `orchestrator/`, `api/` |
| `401 AuthenticationError` | Correct international endpoint set in code — see step 4 above |
| API key not loading | `load_dotenv()` called at the top of `orchestrator.py` and `benchmark.py` before any API calls |
| Running scripts from wrong folder | Always run commands from the **repository root** — the folder containing `main.py` |

---

## Architecture

See the full diagram in `architecture_diagram.html` — includes Qwen Cloud, FastAPI backend, SQLite database, Alibaba Cloud OSS, and the minimal frontend, all connected.

---

## Hackathon Criteria — How We Score

| Criterion | Implementation |
|-----------|----------------|
| **Innovation & AI Creativity (30%)** | Custom multi-agent negotiation protocol; Critic-Writer refinement loop; agent-to-agent direct messaging |
| **Technical Depth (30%)** | Modular agent architecture; shared memory system; SQLite persistence; configurable round limits; full audit trail |
| **Problem Value & Impact (25%)** | Benchmark proves measurable quality gain; real-world tasks (reports, analysis, planning) |
| **Presentation & Documentation (15%)** | Architecture diagram above; this README; interactive demo UI; video walkthrough |

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | System info |
| `/status` | GET | Health check |
| `/run` | POST | Submit a task |
| `/demo` | GET | Run preset demo |
| `/sessions` | GET | List past sessions from the database |

**Example request:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyse the competitive landscape for no-code AI tools", "max_rounds": 2}'
```

---

## Alibaba Cloud Integration

- **Qwen Cloud (DashScope)** — All 5 agents use `qwen-plus` model via the OpenAI-compatible international endpoint
- **Alibaba Cloud ECS** — API server hosted on `ecs.c7.xlarge` (Singapore region)
- **Alibaba Cloud OSS** — Session logs and memory snapshots mirrored to OSS bucket
- **SQLite** — Local persistence layer, mirrored to OSS for durability
- See `alibaba_cloud_deploy.py` for full deployment code and instructions

---

## Track 3 Requirements — Checklist

- [x] **Multiple agents with distinct capabilities** — 5 specialized agents
- [x] **Task decomposition and role assignment** — Planner explicitly assigns subtasks
- [x] **Dialogue and negotiation** — Critic-Writer refinement loop
- [x] **Conflict resolution** — Critic scores and Writer must address all critique points
- [x] **Measurable efficiency gain** — `benchmark.py` compares multi-agent vs single-agent
- [x] **Qwen Cloud** — All LLM calls go through DashScope API
- [x] **Alibaba Cloud deployment** — ECS + OSS integration
- [x] **Database persistence** — SQLite session history
- [x] **Frontend** — Minimal web UI in `frontend/index.html`
- [x] **Architecture diagram** — Includes database and frontend layers
- [x] **Open source license** — MIT License
- [x] **Public code repository** — This repo
- [x] **Verified installation steps** — Tested end-to-end, documented above

---

## License

MIT License — see `LICENSE` file.
