from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from .data import APPLICATION_QUALITY, RQ1_MIXED_FAULTS, RQ2_RECOVERY, RQ4_OVERHEAD

def _configure_matplotlib(font_size: int = 18) -> None:
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman"],
            "font.size": font_size,
        }
    )

def _save(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)

def plot_eval_tcr_fdr(output_dir: Path) -> None:
    _configure_matplotlib(font_size=24)
    fig1, ax1 = plt.subplots(figsize=(18, 7))
    
    methods = ['Erasure Coding', 'Post Mortem', 'Service Mesh', 'Actor Supervision', 'Agent Heuristic', 'AgentMark']
    fdr = [0.0, 0.0, 12.5, 45.0, 68.2, 98.7]
    tcr = [34.2, 34.2, 34.5, 41.0, 52.3, 96.5]
    
    colors = ['#cccccc', '#8c8c8c', '#c887b4', '#2e7d32', '#4b72b0', 'sandybrown']
    hatches = ['-', '+', 'x', '\\', '/', '|']
    
    width = 0.12
    x = np.array([0, 1])
    
    for i in range(len(methods)):
        offset = (i - 2.5) * width
        ax1.bar(0 + offset, fdr[i], width, color=colors[i], edgecolor='white', hatch=hatches[i], label=methods[i])
        ax1.bar(1 + offset, tcr[i], width, color=colors[i], edgecolor='white', hatch=hatches[i])
        
    ax1.set_ylabel('Percentage (%)', fontsize=28)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['Fault Detection Rate (FDR)', 'Task Completion Rate (TCR)'], fontsize=28)
    ax1.set_ylim(0, 100)
    ax1.grid(True, axis='y', linestyle='--', color='gray', alpha=0.7)
    ax1.tick_params(labelsize=24)
    
    handles, labels = ax1.get_legend_handles_labels()
    fig1.legend(handles[:6], labels[:6], loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3, frameon=True, edgecolor='black', fontsize=22)
    
    plt.tight_layout(rect=[0, 0, 1, 0.9])
    _save(fig1, output_dir, "eval_tcr_fdr")

def plot_eval_rollback_efficiency(output_dir: Path) -> None:
    _configure_matplotlib(font_size=24)
    fig2, ax1 = plt.subplots(figsize=(18, 7))
    ax2 = ax1.twinx()
    
    methods = ['Erasure Coding', 'Post Mortem', 'Service Mesh', 'Actor Supervision', 'Agent Heuristic', 'AgentMark']
    duplicate_rate = [100.0, 100.0, 100.0, 100.0, 100.0, 0.0]
    mttr = [0.0, 0.0, 0.0, 22.5, 25.0, 1.4]
    
    colors = ['#cccccc', '#8c8c8c', '#c887b4', '#2e7d32', '#4b72b0', 'sandybrown']
    hatches = ['-', '+', 'x', '\\', '/', '|']
    
    width = 0.12
    
    for i in range(len(methods)):
        offset = (i - 2.5) * width
        ax1.bar(0 + offset, duplicate_rate[i], width, color=colors[i], edgecolor='white', hatch=hatches[i], label=methods[i])
        ax2.bar(1 + offset, mttr[i], width, color=colors[i], edgecolor='white', hatch=hatches[i])
        
        if mttr[i] == 0.0:
            ax2.text(1 + offset, 2.0, 'N/A', ha='center', va='bottom', fontsize=18, color='#c0392b', rotation=90)
            
    ax1.set_ylabel('Percentage (%)', fontsize=28)
    ax2.set_ylabel('Time (s)', fontsize=28)
    
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['Duplicate Side-Effects (%)', 'MTTR (seconds)'], fontsize=28)
    
    ax1.set_ylim(0, 100)
    ax2.set_ylim(0, 30)
    ax2.set_yticks([0, 6, 12, 18, 24, 30])
    
    ax1.grid(True, axis='y', linestyle='--', color='gray', alpha=0.7)
    ax1.tick_params(labelsize=24)
    ax2.tick_params(labelsize=24)
    
    ax1.axvline(0.5, color='gray', linestyle='-.', alpha=0.5)
    
    handles, labels = ax1.get_legend_handles_labels()
    fig2.legend(handles[:6], labels[:6], loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3, frameon=True, edgecolor='black', fontsize=22)
    
    plt.tight_layout(rect=[0, 0, 1, 0.9])
    _save(fig2, output_dir, "eval_rollback_efficiency")

def plot_eval_ablation_timeline(output_dir: Path) -> None:
    _configure_matplotlib(font_size=28)
    fig, ax = plt.subplots(figsize=(12, 6))
    
    methods = ['Erasure Coding', 'Post Mortem', 'Service Mesh', 'Actor Supervision', 'Agent Heuristic', 'AgentMark (Ours)']
    y_pos = np.arange(len(methods)) * 2
    
    phases = {
        'Execution': '#cccccc',
        'Network Interception': '#c887b4',
        'Supervision': '#2e7d32',
        'LLM Reflection': '#4b72b0',
        'AgentMark': 'sandybrown',
        'Verification': '#e67e22'
    }
    
    timeline_data = {
        'Erasure Coding': [(0, 5, 'Execution'), (5, 1.5, 'Network Interception')],
        'Post Mortem': [(0, 5, 'Execution'), (5, 0.5, 'Supervision')],
        'Service Mesh': [(0, 1.5, 'Network Interception'), (1.5, 5, 'Execution'), (6.5, 1.0, 'Network Interception')],
        'Actor Supervision': [(0, 2.5, 'Supervision'), (2.5, 5, 'Execution'), (7.5, 2.5, 'Supervision')],
        'Agent Heuristic': [(0, 5, 'Execution'), (5, 20, 'LLM Reflection')],
        'AgentMark (Ours)': [(0, 1.2, 'AgentMark'), (1.2, 5, 'Execution'), (6.2, 2.5, 'AgentMark'), (8.7, 3.8, 'AgentMark'), (12.5, 1.0, 'Verification')]
    }
    
    bar_height = 0.8
    for i, method in enumerate(methods):
        tasks = timeline_data[method]
        for task in tasks:
            start, duration, phase = task
            color = phases[phase]
            rect = mpatches.Rectangle((start, y_pos[i] - bar_height/2), duration, bar_height, 
                                      facecolor=color, edgecolor='white', linewidth=1, alpha=0.9)
            ax.add_patch(rect)
            
    ax.set_yticks(y_pos)
    ax.set_yticklabels(methods, fontsize=26)
    ax.set_xlabel('Operating Time', fontsize=30)
    ax.set_ylim(-1.5, y_pos[-1] + 1.5)
    ax.set_xlim(0, 30)
    
    ax.xaxis.grid(True, linestyle=':', color='gray', alpha=0.6)
    ax.yaxis.grid(False)
    ax.set_xticklabels([])
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    legend_patches = [mpatches.Patch(color=color, label=label, alpha=0.9) for label, color in phases.items()]
    ax.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, 1.05), ncol=3, frameon=True, edgecolor='black', fontsize=20)

    fig.subplots_adjust(left=0.35, right=0.98, bottom=0.15, top=0.75)
    _save(fig, output_dir, "eval_ablation_timeline")

def plot_eval_scalability_payload(output_dir: Path) -> None:
    _configure_matplotlib(font_size=24)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    payload_sizes = ['1KB', '10KB', '100KB', '1MB', '10MB']
    
    vanilla_rpc = [2.1, 4.5, 12.3, 45.8, 210.5]
    agentmark_rpc = [8.5, 11.2, 19.8, 56.4, 225.1]
    
    ax1.plot(payload_sizes, vanilla_rpc, marker='o', linestyle='--', color='gray', linewidth=2, markersize=12, label='Vanilla RPC')
    ax1.plot(payload_sizes, agentmark_rpc, marker='s', linestyle='-', color='sandybrown', linewidth=3, markersize=12, label='AgentMark (Ours)')
    
    ax1.set_xlabel('Communication Payload Size', fontsize=28)
    ax1.set_ylabel('End-to-End Latency (ms)', fontsize=28)
    ax1.set_yscale('log')
    ax1.grid(True, axis='y', linestyle='--', color='gray', alpha=0.7)
    ax1.tick_params(labelsize=24)
    ax1.legend(loc='upper left', frameon=True, edgecolor='black', fontsize=22)
    
    fig1.subplots_adjust(left=0.18, right=0.98, bottom=0.22, top=0.93)
    _save(fig1, output_dir, "eval_scalability_payload")

def write_tables(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "general_performance.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Method", "FDR", "TCR"])
        writer.writerows(zip(RQ1_MIXED_FAULTS["methods"], RQ1_MIXED_FAULTS["fdr"], RQ1_MIXED_FAULTS["tcr"]))

def generate_all_figures(output_dir: str | Path) -> None:
    output_path = Path(output_dir)
    plot_eval_tcr_fdr(output_path)
    plot_eval_rollback_efficiency(output_path)
    plot_eval_ablation_timeline(output_path)
    plot_eval_scalability_payload(output_path)
    write_tables(output_path)

if __name__ == "__main__":
    generate_all_figures(Path("outputs/full/figures"))
