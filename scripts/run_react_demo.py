import sys
import json
from pathlib import Path

# Ensure src is in PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from agentmark_repro.frameworks import run_unified_react_demo

if __name__ == "__main__":
    print("Running unified ReAct framework demo for LangChain and AgentScope...")
    results = run_unified_react_demo("Book a flight to Tokyo and reserve a hotel.")
    print(json.dumps(results, indent=2))
