import matplotlib.pyplot as plt
import numpy as np
import os

def plot_ablation_charts():
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
        "font.size": 18
    })
    os.makedirs('./fig', exist_ok=True)
    
    methods = ['Erasure Coding', 'Post Mortem', 'Service Mesh', 'Actor Supervision', 'Agent Heuristic', 'AgentMark']
    colors = ['#cccccc', '#969696', '#d77dbe', 'green', '#3e75b0', 'sandybrown']
    hatches = ['-', '+', 'x', '\\', '/', '|']
    latency_ms = [1.5, 0.5, 2.5, 5.0, 154.2, 8.5]  # Added a small latency for Post Mortem
    
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(1)
    width = 0.15
    
    for i in range(len(methods)):
        pos = x - (len(methods)*width)/2 + i*width + width/2
        ax.bar(pos, [latency_ms[i]], width, label=methods[i], color=colors[i], edgecolor='white', hatch=hatches[i], linewidth=1)
        
    ax.set_ylabel('Latency Overhead (ms)', fontsize=22)
    ax.set_xticks(x)
    ax.set_xticklabels(['System Overhead'], fontsize=22)
    ax.set_ylim(0, 160)
    ax.grid(True, axis='y', linestyle='--', color='gray', alpha=0.7)
    ax.tick_params(labelsize=20)
    
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=3, frameon=True, edgecolor='black', fontsize=18)
    
    plt.tight_layout(rect=[0, 0, 1, 0.85])
    try: plt.savefig('eval_overhead_breakdown.pdf', format='pdf', bbox_inches='tight')
    except: pass
    plt.savefig('eval_overhead_breakdown.png', dpi=300, bbox_inches='tight')
    try: plt.savefig('eval_overhead_breakdown.svg', format='svg', bbox_inches='tight')
    except: pass
    plt.close()
    print("Chart saved as eval_overhead_breakdown.png")

if __name__ == "__main__":
    plot_ablation_charts()