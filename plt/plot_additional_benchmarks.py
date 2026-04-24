import matplotlib.pyplot as plt
import numpy as np
import os

def plot_additional_benchmarks():
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
        "font.size": 18
    })
    os.makedirs('./fig', exist_ok=True)
    
    # ==========================================
    # 1. Scalability: Overhead vs. Payload Size
    # ==========================================
    fig1, ax1 = plt.subplots(figsize=(8.4, 5.6))
    payload_sizes = ['1KB', '10KB', '100KB', '1MB', '10MB']
    
    # Simulated latency (ms)
    vanilla_rpc = [2.1, 4.5, 12.3, 45.8, 210.5]
    agentmark_rpc = [8.5, 11.2, 19.8, 56.4, 225.1]
    
    ax1.plot(payload_sizes, vanilla_rpc, marker='o', linestyle='--', color='gray', linewidth=2, markersize=10, label='Vanilla RPC')
    ax1.plot(payload_sizes, agentmark_rpc, marker='s', linestyle='-', color='sandybrown', linewidth=3, markersize=10, label='AgentMark (Ours)')
    
    ax1.set_xlabel('Communication Payload Size', fontsize=22)
    ax1.set_ylabel('End-to-End Latency (ms)', fontsize=22)
    ax1.set_yscale('log') # Log scale is better for payload growth
    ax1.grid(True, axis='y', linestyle='--', color='gray', alpha=0.7)
    ax1.tick_params(labelsize=20)
    ax1.legend(loc='upper left', frameon=True, edgecolor='black', fontsize=18)
    
    # Match the canvas geometry used by the timeline figure so both figures
    # align cleanly across columns in the paper layout.
    fig1.subplots_adjust(left=0.18, right=0.98, bottom=0.22, top=0.93)
    try: plt.savefig('./fig/eval_scalability_payload.pdf', format='pdf')
    except: pass
    plt.savefig('./fig/eval_scalability_payload.png', dpi=300)
    plt.close()
    
    # ==========================================
    # 2. Component Ablation: Where does the 8.5ms go?
    # ==========================================
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    components = ['W_infra\n(Hardware)', 'W_exec\n(Runtime)', 'W_sem\n(LLM/API)', 'Verification']
    latency_breakdown = [1.2, 2.5, 3.8, 1.0] # Sums to 8.5ms
    
    x = np.arange(len(components))
    bars = ax2.bar(x, latency_breakdown, width=0.5, color='#3e75b0', edgecolor='black', hatch='/', linewidth=1.5)
    
    for bar in bars:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f'{yval}ms', ha='center', va='bottom', fontsize=18)
        
    ax2.set_ylabel('Latency Overhead (ms)', fontsize=22)
    ax2.set_xticks(x)
    ax2.set_xticklabels(components, fontsize=20)
    ax2.set_ylim(0, 5)
    ax2.grid(True, axis='y', linestyle='--', color='gray', alpha=0.7)
    ax2.tick_params(labelsize=20)
    
    plt.tight_layout()
    try: plt.savefig('./fig/eval_ablation_latency.pdf', format='pdf', bbox_inches='tight')
    except: pass
    plt.savefig('./fig/eval_ablation_latency.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    plot_additional_benchmarks()
