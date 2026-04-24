import sys
from pathlib import Path

# Ensure src is in PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from agentmark_repro import run_full_reproduction, generate_all_figures

if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parents[1] / "outputs" / "full"
    print("Running full reproduction (this will simulate data and generate figures)...")
    run_full_reproduction(output_dir)
    print(f"Results saved to {output_dir}/full_results.json")
    
    figures_dir = output_dir / "figures"
    generate_all_figures(figures_dir)
    print(f"All figures generated in {figures_dir}")
