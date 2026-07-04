"""
Agent Society — Main Entry Point
----------------------------------
Run this to see the full system in action from the terminal.

Usage:
  python main.py                          # Interactive mode
  python main.py --task "Your task here"  # Direct task mode
  python main.py --demo                   # Run a preset demo task
  python main.py --benchmark              # Run the benchmark comparison
"""

import argparse
import json
import sys
import os

# Make sure all modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator.orchestrator import AgentSocietyOrchestrator


def print_result(result: dict):
    """Pretty-print the final result bundle."""
    print("\n" + "=" * 60)
    print("🏆 AGENT SOCIETY — FINAL RESULT")
    print("=" * 60)

    print(f"\n📊 EFFICIENCY: {result['efficiency_gain']}")
    print(f"🔄 ROUNDS COMPLETED: {result['rounds_completed']}")

    print("\n📋 PLAN GENERATED:")
    print("-" * 40)
    print(result["plan"])

    print("\n🔍 RESEARCH SUMMARY:")
    print("-" * 40)
    print(result["research_summary"])

    print("\n✅ FINAL OUTPUT:")
    print("=" * 60)
    print(result["final_output"])

    print("\n💬 AGENT CONVERSATION LOG:")
    print("-" * 40)
    for entry in result["conversation_log"]:
        print(f"  [{entry['from'].upper()} → {entry['to'].upper()}]")
        print(f"  {entry['message'][:200]}...")
        print()


def main():
    parser = argparse.ArgumentParser(description="Agent Society — Multi-Agent AI System")
    parser.add_argument("--task", type=str, help="Task to run")
    parser.add_argument("--demo", action="store_true", help="Run preset demo")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    parser.add_argument("--rounds", type=int, default=3, help="Max critique rounds")
    args = parser.parse_args()

    if args.benchmark:
        from benchmark import run_benchmark
        run_benchmark()
        return

    if args.demo:
        task = (
            "Analyse the business opportunity for an AI-powered legal document "
            "review tool targeting small law firms in emerging markets. Include "
            "market size, key risks, competitive landscape, and go-to-market strategy."
        )
    elif args.task:
        task = args.task
    else:
        print("🤖 AGENT SOCIETY — Interactive Mode")
        print("Enter your task (or press Ctrl+C to quit):")
        try:
            task = input(">>> ").strip()
            if not task:
                print("No task provided. Exiting.")
                return
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return

    orchestrator = AgentSocietyOrchestrator()
    result = orchestrator.run(task, max_rounds=args.rounds)
    print_result(result)

    # Export memory snapshot for demo/judging
    orchestrator.memory.export_snapshot("session_snapshot.json")
    print("\n📁 Memory snapshot saved to session_snapshot.json")


if __name__ == "__main__":
    main()
