import sys
from pathlib import Path

# Ensure src is in PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from agentmark_repro import run_minimal_reproduction

if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parents[1] / "outputs" / "minimal"
    run_minimal_reproduction(output_dir)
    print(f"Minimal reproduction complete. Check {output_dir}/minimal_summary.json")
