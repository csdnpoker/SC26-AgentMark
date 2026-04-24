import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

def plot_timeline_ablation():
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
        "font.size": 32  # Increased base font size significantly
    })
    os.makedirs('./fig', exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    
    # Methods on Y-axis
    methods = ['Erasure Coding', 'Post Mortem', 'Service Mesh', 'Actor Supervision', 'Agent Heuristic', 'AgentMark (Ours)']
    y_pos = np.arange(len(methods)) * 2  # Space out the rows
    
    # Define phases and colors
    phases = {
        'Execution': '#cccccc',           # Gray
        'Network Interception': '#d77dbe',        # Pink/Purple
        'Supervision': '#2ca02c', # Green
        'LLM Reflection': '#3e75b0',      # Blue
        'AgentMark': 'sandybrown', # Orange
        'Verification': '#ff7f0e' # Darker Orange
    }
    
    # Data: List of tuples for each method (start_time, duration, phase_name)
    # Ensuring no overlaps and comprehensive steps for each baseline
    timeline_data = {
        'Erasure Coding': [
            (0, 5, 'Execution'), 
            (5, 1.5, 'Network Interception') 
        ],
        'Post Mortem': [
            (0, 5, 'Execution'), 
            (5, 0.5, 'Supervision') 
        ],
        'Service Mesh': [
            (0, 1.5, 'Network Interception'), 
            (1.5, 5, 'Execution'), 
            (6.5, 1.0, 'Network Interception') 
        ],
        'Actor Supervision': [
            (0, 2.5, 'Supervision'), 
            (2.5, 5, 'Execution'), 
            (7.5, 2.5, 'Supervision') 
        ],
        'Agent Heuristic': [
            (0, 5, 'Execution'), 
            (5, 20, 'LLM Reflection') # Cap visual length, we won't label time
        ],
        'AgentMark (Ours)': [
            (0, 1.2, 'AgentMark'), # W_infra
            (1.2, 5, 'Execution'), 
            (6.2, 2.5, 'AgentMark'), # W_exec
            (8.7, 3.8, 'AgentMark'), # W_sem
            (12.5, 1.0, 'Verification') # Verification
        ]
    }
    
    # Draw the Gantt chart blocks
    bar_height = 0.8
    
    for i, method in enumerate(methods):
        tasks = timeline_data[method]
        for task in tasks:
            start, duration, phase = task
            color = phases[phase]
            
            rect = mpatches.Rectangle((start, y_pos[i] - bar_height/2), duration, bar_height, 
                                      facecolor=color, edgecolor='white', linewidth=1, alpha=0.85)
            ax.add_patch(rect)
            
    # Formatting
    ax.set_yticks(y_pos)
    # Remove fontweight='bold' to match the payload plot's normal weight
    ax.set_yticklabels(methods, fontsize=32)
    ax.set_xlabel('Operating Time', fontsize=36)
    
    # Set y limits to add space at the top and bottom (added more space at the top for legend)
    ax.set_ylim(-1.5, y_pos[-1] + 1.5)
    
    # X-axis limits (capping to show detail without letting the 150ms squish everything)
    ax.set_xlim(0, 30)
    
    # Grid lines for time
    ax.xaxis.grid(True, linestyle=':', color='gray', alpha=0.6)
    ax.yaxis.grid(False)
    
    # Remove x-axis tick labels (numbers) since we just want to show the flow
    ax.set_xticklabels([])
    
    # Hide top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Create custom legend
    legend_patches = [mpatches.Patch(color=color, label=label, alpha=0.85) for label, color in phases.items()]
    # Move legend back to top, adjust bbox_to_anchor to ensure clear spacing from the top bar
    ax.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, 1.03), ncol=3, frameon=True, edgecolor='black', fontsize=16)

    # Use an explicit canvas and fixed margins so the exported figure aligns
    # with other single-column figures in the paper.
    fig.subplots_adjust(left=0.27, right=0.98, bottom=0.19, top=0.80)
    try: plt.savefig('./fig/eval_ablation_timeline.pdf', format='pdf')
    except: pass
    plt.savefig('./fig/eval_ablation_timeline.png', dpi=300)
    try: plt.savefig('./fig/eval_ablation_timeline.svg', format='svg')
    except: pass
    plt.close()
    print("Timeline generated.")

if __name__ == "__main__":
    plot_timeline_ablation()
