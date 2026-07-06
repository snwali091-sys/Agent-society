"""
View Sessions
-------------
A simple CLI tool to browse past Agent Society runs saved in the database.

Usage:
    python view_sessions.py              # list all sessions
    python view_sessions.py --id 3       # view full detail of session #3
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from database.db import get_all_sessions, get_session


def list_sessions():
    sessions = get_all_sessions()
    if not sessions:
        print("No sessions found yet. Run 'python main.py --demo' first.")
        return

    print(f"\n📚 {len(sessions)} saved session(s):\n")
    for s in sessions:
        print(f"  #{s['id']} | {s['task'][:60]}...")
        print(f"      Rounds: {s['rounds_completed']} | {s['efficiency_gain']}")
        print()


def show_session(session_id: int):
    s = get_session(session_id)
    if not s:
        print(f"No session found with ID {session_id}")
        return

    print(f"\n{'='*60}")
    print(f"SESSION #{s['id']}")
    print(f"{'='*60}")
    print(f"\nTASK: {s['task']}")
    print(f"\nPLAN:\n{s['plan']}")
    print(f"\nRESEARCH:\n{s['research']}")
    print(f"\nFINAL OUTPUT:\n{s['final_output']}")
    print(f"\nROUNDS: {s['rounds_completed']} | EFFICIENCY: {s['efficiency_gain']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View saved Agent Society sessions")
    parser.add_argument("--id", type=int, help="View a specific session by ID")
    args = parser.parse_args()

    if args.id:
        show_session(args.id)
    else:
        list_sessions()
