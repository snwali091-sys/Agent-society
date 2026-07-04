"""
Shared Memory
-------------
The WHITEBOARD that all agents can read and write.

This is what makes it a "society" rather than isolated agents —
they share a common knowledge space.

What gets stored:
  - The original task (so every agent always knows the goal)
  - The plan (Planner writes, everyone reads)
  - Research data (Researcher writes, Writer reads)
  - Drafts (Writer writes, Critic reads)
  - Critiques (Critic writes, Writer reads)
  - Final output (Executor writes)

In production, you'd replace this with:
  - Redis (for distributed multi-machine deployments)
  - PostgreSQL (for persistence across sessions)
  - Vector DB like Milvus (for semantic memory retrieval)
"""

import json
import time
from typing import Any, Optional, List


class SharedMemory:
    def __init__(self):
        self._store = {}       # Main key-value store
        self._history = []     # Full audit log of all writes
        self._created_at = time.time()

    # ── BASIC OPERATIONS ──────────────────────────────────────────────────────

    def set(self, key: str, value: Any) -> None:
        """Store a value. Any agent can call this."""
        self._store[key] = value
        self._history.append({
            "timestamp": time.time() - self._created_at,
            "action": "SET",
            "key": key,
            "preview": str(value)[:100] + "..." if len(str(value)) > 100 else str(value),
        })

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value. Returns default if key doesn't exist."""
        return self._store.get(key, default)

    def delete(self, key: str) -> None:
        """Remove a key (e.g., clear outdated drafts)."""
        if key in self._store:
            del self._store[key]

    # ── INSPECTION & DEBUGGING ────────────────────────────────────────────────

    def get_all(self) -> dict:
        """Dump everything — useful for debugging or exporting state."""
        return dict(self._store)

    def get_history(self) -> List[dict]:
        """Full audit trail of every read/write operation."""
        return list(self._history)

    def summary(self) -> str:
        """Human-readable summary of what's in memory."""
        lines = ["📋 SHARED MEMORY CONTENTS:"]
        for key, value in self._store.items():
            preview = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
            lines.append(f"  [{key}]: {preview}")
        return "\n".join(lines)

    # ── SNAPSHOT (for hackathon demo) ─────────────────────────────────────────

    def export_snapshot(self, filepath: str = "memory_snapshot.json") -> None:
        """
        Export the full memory state to JSON.
        Useful for the hackathon demo — proves agents actually
        shared state across a session.
        """
        snapshot = {
            "timestamp": time.time(),
            "session_duration_seconds": time.time() - self._created_at,
            "keys_stored": list(self._store.keys()),
            "write_operations": len(self._history),
            "history": self._history,
        }
        with open(filepath, "w") as f:
            json.dump(snapshot, f, indent=2)
        print(f"✅ Memory snapshot exported to {filepath}")
