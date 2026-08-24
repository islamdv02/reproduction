"""
Figure 5 Publication-Quality Multi-Panel Generator: Cell-Type Perturbations.
Faithfully reproduces Figure 5 of Komi et al., Nature Communications, 2026:
- 5A: Spatial projectome profile before & after V1 ablation (rostral inhibitory lobe loss)
- 5B: Spatiotemporal traveling wave & synthetic EMG during V1 perturbation (frequency slowdown & hyperflexion)
- 5C: V1 quantification bar charts (frequency, amplitude) and polar phase coordination
- 5D: Contralateral projectome profile before & after V0 ablation (loss of commissural wiring)
- 5E: Spatiotemporal traveling wave & synthetic EMG during V0 perturbation (bilateral synchronous hopping)
- 5F: V0 quantification bar charts and polar phase transition (left-right alternation -> synchrony)
- Composite Figure 5: Unified 6-panel publication figure
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List

from locomotion import generate_synthetic_emg, MUSCLE_FLEX_EXT
from figure3_analysis import POP_COLORS, MUSCLE_COLORS


def compute_projectome_1d_profile(
    network: Any,
    target_pop: Optional[str] = None,
    bin_size_um: float = 200.0,
    max_dist_um: float = 4000.0,
    contralateral_only: bool = False
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes the 1D spatial projectome weight distribution as a function of
    rostrocaudal distance (Z_post - Z_pre) matching MATLAB GenerateSynapticDistrib.m.
    """
    W = network.conn_mat
    pos_z = network.pos_z
    latera = network.latera

    # Determine source neurons
    if target_pop:
        src_mask = (network.types == target_pop)
    else:
        src_mask = np.ones(network.n_neurons, dtype=bool)

    if contralateral_only:
        # Cross-cord connections
        lat_diff = (latera[:, None] != latera[None, :])
        active_W = W * lat_diff
    else:
        active_W = W

    active_W = active_W[:, src_mask]
    src_z = pos_z[src_mask]

    # Pre-calculate pairwise delta Z
    delta_z_mat = pos_z[:, None] - src_z[None, :]

    bins = np.arange(-max_dist_um, max_dist_um + bin_size_um, bin_size_um)
    bin_centers = (bins[:-1] + bins[1:]) / 2.0
    profile = np.zeros(len(bin_centers), dtype=np.float64)

    non_zero = (active_W != 0)
    if np.any(non_zero):
        dz_vals = delta_z_mat[non_zero]
        w_vals = active_W[non_zero]

        bin_idx = np.digitize(dz_vals, bins) - 1
        valid = (bin_idx >= 0) & (bin_idx < len(bin_centers))
        for idx in range(len(bin_centers)):
            m = (bin_idx == idx) & valid
            if np.any(m):
                profile[idx] = np.sum(w_vals[m])

    return bin_centers, profile


def plot_panel_5a_v1_projectome(
    control_net: Any,
    v1_net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 5A: Spatial projectome profile before vs after V1 deletion.
    Illustrates the selective attenuation of the rostral inhibitory lobe (sp2).
    """
    fig, ax = plt.subplots(figsize=(7, 5), dpi=dpi)

    dz_ctrl, prof_ctrl = compute_projectome_1d_profile(control_net, target_pop='V1')
    dz_v1, prof_v1 = compute_projectome_1d_profile(v1_net, target_pop='V1')
    _, prof_all_ctrl = compute_projectome_1d_profile(control_net)
    _, prof_all_v1 = compute_projectome_1d_profile(v1_net)

    ax.plot(dz_ctrl, prof_all_ctrl, color='#333333', linewidth=2.0, label='Control Projectome')
    ax.plot(dz_v1, prof_all_v1, color='#d95f02', linewidth=2.2, linestyle='--', label='V1 Ablated Projectome')
    ax.fill_between(dz_ctrl, prof_ctrl, 0, color='#377eb8', alpha=0.3, label='V1 Rostral Inhibitory Lobe ($sp_2$)')

    ax.axvline(0, color='#888888', linestyle=':', alpha=0.7)
    ax.axhline(0, color='#888888', linestyle='-', alpha=0.5)

    ax.set_xlabel('Rostrocaudal Distance $\\Delta Z$ (µm)\n(Caudal $\\leftarrow 0 \\rightarrow$ Rostral)', fontsize=10.5, fontweight='bold')
    ax.set_ylabel('Net Synaptic Weight (a.u.)', fontsize=10.5, fontweight='bold')
    ax.set_title('Figure 5A: V1 Removal Eliminates Rostral Inhibitory Lobe', fontsize=11.5, fontweight='bold', pad=10)
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.legend(loc='upper right', fontsize=9, frameon=True)

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_5b_v1_activity_emg(
    control_res: Any,
    v1_res: Any,
    control_net: Any,
    v1_net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 5B: Spatiotemporal traveling wave and synthetic EMG comparison (Control vs V1).
    Demonstrates cycle prolongation (slowdown) and increased motor amplitude (hyperflexion).
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.5), dpi=dpi, sharex=True)

    t_mask = (control_res.time_ms >= 4000) & (control_res.time_ms <= 6000)
    t_sec = (control_res.time_ms[t_mask] - 4000) / 1000.0

    # Control synthetic EMG
    emg_ctrl = generate_synthetic_emg(
        rates=control_res.rates,
        neuron_types=control_net.types,
        neuron_lat=control_net.latera,
        neuron_z=control_net.pos_z,
        time_ms=control_res.time_ms,
        noise_level=0.15,
        window_ms=20,
        rng_seed=42
    )

    # V1 Perturbation synthetic EMG
    emg_v1 = generate_synthetic_emg(
        rates=v1_res.rates,
        neuron_types=v1_net.types,
        neuron_lat=v1_net.latera,
        neuron_z=v1_net.pos_z,
        time_ms=v1_res.time_ms,
        noise_level=0.15,
        window_ms=20,
        rng_seed=42
    )

    # Plot Control
    offset = 0.0
    for side in ['Left', 'Right']:
        for m_name in ['Tibialis Anterior', 'Gastrocnemius']:
            if side in emg_ctrl and m_name in emg_ctrl[side]['muscles']:
                idx = list(emg_ctrl[side]['muscles']).index(m_name)
                env = emg_ctrl[side]['envelope'][t_mask, idx]
                col = MUSCLE_COLORS['Flex'] if 'Tibialis' in m_name else MUSCLE_COLORS['Ext']
                ls = '-' if side == 'Left' else '--'
                ax1.plot(t_sec, env + offset, color=col, linestyle=ls, lw=1.8, label=f"{side[0]} {m_name}")
                offset += 1.0

    ax1.set_title('Control: Normal Locomotion ($I_e = 30$ pA)', fontsize=11, fontweight='bold', pad=6)
    ax1.set_ylabel('Synthetic EMG (a.u.)', fontsize=9.5, fontweight='bold')
    ax1.set_yticks([])
    ax1.grid(True, linestyle=':', alpha=0.4)
    ax1.legend(loc='upper right', fontsize=8, ncol=2, frameon=True)

    # Plot V1 Perturbation
    offset = 0.0
    for side in ['Left', 'Right']:
        for m_name in ['Tibialis Anterior', 'Gastrocnemius']:
            if side in emg_v1 and m_name in emg_v1[side]['muscles']:
                idx = list(emg_v1[side]['muscles']).index(m_name)
                env = emg_v1[side]['envelope'][t_mask, idx]
                col = MUSCLE_COLORS['Flex'] if 'Tibialis' in m_name else MUSCLE_COLORS['Ext']
                ls = '-' if side == 'Left' else '--'
                ax2.plot(t_sec, env + offset, color=col, linestyle=ls, lw=1.8)
                offset += 1.2 * max(float(np.max(env)), 0.5)

    ax2.set_title('V1 Ablation: Rhythm Deceleration & Elevated Burst Amplitude', fontsize=11, fontweight='bold', pad=6)
    ax2.set_xlabel('Time (s)', fontsize=10.5, fontweight='bold')
    ax2.set_ylabel('Synthetic EMG (a.u.)', fontsize=9.5, fontweight='bold')
    ax2.set_yticks([])
    ax2.grid(True, linestyle=':', alpha=0.4)

    plt.suptitle('Figure 5B: V1 Perturbation Slows Rhythm and Increases Burst Amplitude', fontsize=12.5, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_5c_v1_quantification(
    control_metrics: Dict[str, Any],
    v1_metrics: Dict[str, Any],
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 5C: Quantitative comparison of Frequency, Amplitude, and Polar Phases (Control vs V1).
    """
    fig = plt.figure(figsize=(10, 4.5), dpi=dpi)
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.2])

    # 1. Frequency Bar Chart
    ax_f = fig.add_subplot(gs[0, 0])
    bars_f = ax_f.bar(['Control', 'V1 Ablation'], [control_metrics['frequency_hz'], v1_metrics['frequency_hz']],
                      color=['#333333', '#d95f02'], width=0.55, edgecolor='black', lw=1.0)
    ax_f.set_ylabel('Frequency (Hz)', fontsize=10, fontweight='bold')
    ax_f.set_title('Locomotor Frequency', fontsize=10.5, fontweight='bold')
    ax_f.grid(True, linestyle=':', alpha=0.4, axis='y')
    for bar in bars_f:
        yval = bar.get_height()
        ax_f.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, f"{yval:.2f} Hz", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    # 2. RMS Amplitude Bar Chart
    ax_a = fig.add_subplot(gs[0, 1])
    bars_a = ax_a.bar(['Control', 'V1 Ablation'], [control_metrics['rms_amplitude_hz'], v1_metrics['rms_amplitude_hz']],
                      color=['#333333', '#7570b3'], width=0.55, edgecolor='black', lw=1.0)
    ax_a.set_ylabel('RMS Rate Amplitude (Hz)', fontsize=10, fontweight='bold')
    ax_a.set_title('Motor Burst Amplitude', fontsize=10.5, fontweight='bold')
    ax_a.grid(True, linestyle=':', alpha=0.4, axis='y')
    for bar in bars_a:
        yval = bar.get_height()
        ax_a.text(bar.get_x() + bar.get_width()/2.0, yval + 0.002, f"{yval:.3f}", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    # 3. Polar Phase Plot
    ax_p = fig.add_subplot(gs[0, 2], projection='polar')
    for name, m, col in [('Control', control_metrics, '#333333'), ('V1 Ablation', v1_metrics, '#d95f02')]:
        phi_lr = m['lr_phase_rad']
        phi_fe = m['fe_phase_rad']
        ax_p.annotate('', xy=(phi_lr, 0.85), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=2.0))
        ax_p.scatter([phi_lr], [0.85], color=col, s=60, label=f"{name} L-R: {m['lr_phase_deg']:.1f}°")
        ax_p.scatter([phi_fe], [0.55], color=col, marker='s', s=40, label=f"{name} F-E: {m['fe_phase_deg']:.1f}°")

    ax_p.set_title('Phase Coordination\n(Preserved Alternation)', fontsize=10.5, fontweight='bold', pad=12)
    ax_p.set_ylim(0.0, 1.0)
    ax_p.set_yticklabels([])
    ax_p.legend(loc='lower center', bbox_to_anchor=(0.5, -0.4), fontsize=7.5, frameon=True)

    plt.suptitle('Figure 5C: V1 Ablation Quantification', fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_5d_v0_projectome(
    control_net: Any,
    v0_net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 5D: Contralateral projectome profile before vs after V0 deletion.
    Illustrates the collapse of cross-cord commissural connectivity.
    """
    fig, ax = plt.subplots(figsize=(7, 5), dpi=dpi)

    dz_ctrl, prof_ctrl = compute_projectome_1d_profile(control_net, contralateral_only=True)
    dz_v0, prof_v0 = compute_projectome_1d_profile(v0_net, contralateral_only=True)

    ax.plot(dz_ctrl, prof_ctrl, color='#1b9e77', linewidth=2.5, label='Control Contralateral Projectome')
    ax.plot(dz_v0, prof_v0, color='#e7298a', linewidth=2.2, linestyle='--', label='V0 Ablated Contralateral Projectome')
    ax.fill_between(dz_ctrl, prof_ctrl, 0, color='#1b9e77', alpha=0.25, label='V0 Commissural Projectome')

    ax.axvline(0, color='#888888', linestyle=':', alpha=0.7)
    ax.axhline(0, color='#888888', linestyle='-', alpha=0.5)

    ax.set_xlabel('Rostrocaudal Distance $\\Delta Z$ (µm)\n(Caudal $\\leftarrow 0 \\rightarrow$ Rostral)', fontsize=10.5, fontweight='bold')
    ax.set_ylabel('Contralateral Synaptic Weight (a.u.)', fontsize=10.5, fontweight='bold')
    ax.set_title('Figure 5D: V0 Removal Abolishes Contralateral Commissural Coupling', fontsize=11.5, fontweight='bold', pad=10)
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.legend(loc='upper right', fontsize=9, frameon=True)

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_5e_v0_activity_emg(
    control_res: Any,
    v0_res: Any,
    control_net: Any,
    v0_net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 5E: Spatiotemporal traveling wave & synthetic EMG during V0 perturbation.
    Demonstrates the emergence of bilateral in-phase synchrony (hopping gait).
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.5), dpi=dpi, sharex=True)

    t_mask = (control_res.time_ms >= 4000) & (control_res.time_ms <= 6000)
    t_sec = (control_res.time_ms[t_mask] - 4000) / 1000.0

    emg_ctrl = generate_synthetic_emg(
        rates=control_res.rates,
        neuron_types=control_net.types,
        neuron_lat=control_net.latera,
        neuron_z=control_net.pos_z,
        time_ms=control_res.time_ms,
        noise_level=0.15,
        window_ms=20,
        rng_seed=42
    )

    emg_v0 = generate_synthetic_emg(
        rates=v0_res.rates,
        neuron_types=v0_net.types,
        neuron_lat=v0_net.latera,
        neuron_z=v0_net.pos_z,
        time_ms=v0_res.time_ms,
        noise_level=0.15,
        window_ms=20,
        rng_seed=42
    )

    # Plot Control
    offset = 0.0
    for side in ['Left', 'Right']:
        for m_name in ['Tibialis Anterior', 'Gastrocnemius']:
            if side in emg_ctrl and m_name in emg_ctrl[side]['muscles']:
                idx = list(emg_ctrl[side]['muscles']).index(m_name)
                env = emg_ctrl[side]['envelope'][t_mask, idx]
                col = MUSCLE_COLORS['Flex'] if 'Tibialis' in m_name else MUSCLE_COLORS['Ext']
                ls = '-' if side == 'Left' else '--'
                ax1.plot(t_sec, env + offset, color=col, linestyle=ls, lw=1.8, label=f"{side[0]} {m_name}")
                offset += 1.0

    ax1.set_title('Control: Left–Right Alternation ($I_e = 30$ pA)', fontsize=11, fontweight='bold', pad=6)
    ax1.set_ylabel('Synthetic EMG (a.u.)', fontsize=9.5, fontweight='bold')
    ax1.set_yticks([])
    ax1.grid(True, linestyle=':', alpha=0.4)
    ax1.legend(loc='upper right', fontsize=8, ncol=2, frameon=True)

    # Plot V0 Perturbation
    offset = 0.0
    for side in ['Left', 'Right']:
        for m_name in ['Tibialis Anterior', 'Gastrocnemius']:
            if side in emg_v0 and m_name in emg_v0[side]['muscles']:
                idx = list(emg_v0[side]['muscles']).index(m_name)
                env = emg_v0[side]['envelope'][t_mask, idx]
                col = MUSCLE_COLORS['Flex'] if 'Tibialis' in m_name else MUSCLE_COLORS['Ext']
                ls = '-' if side == 'Left' else '--'
                ax2.plot(t_sec, env + offset, color=col, linestyle=ls, lw=1.8)
                offset += 1.2 * max(float(np.max(env)), 0.5)

    ax2.set_title('V0 Ablation: Synchronous Hopping / Bounding Gait Phenotype', fontsize=11, fontweight='bold', pad=6)
    ax2.set_xlabel('Time (s)', fontsize=10.5, fontweight='bold')
    ax2.set_ylabel('Synthetic EMG (a.u.)', fontsize=9.5, fontweight='bold')
    ax2.set_yticks([])
    ax2.grid(True, linestyle=':', alpha=0.4)

    plt.suptitle('Figure 5E: V0 Perturbation Converts Alternating Gait to Bilateral Synchrony (Hopping)', fontsize=12.5, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_5f_v0_quantification(
    control_metrics: Dict[str, Any],
    v0_metrics: Dict[str, Any],
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 5F: Quantitative comparison of Frequency and Polar Phase Transition (Control vs V0).
    """
    fig = plt.figure(figsize=(10, 4.5), dpi=dpi)
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.2])

    # 1. Frequency Bar Chart
    ax_f = fig.add_subplot(gs[0, 0])
    bars_f = ax_f.bar(['Control', 'V0 Ablation'], [control_metrics['frequency_hz'], v0_metrics['frequency_hz']],
                      color=['#333333', '#e7298a'], width=0.55, edgecolor='black', lw=1.0)
    ax_f.set_ylabel('Frequency (Hz)', fontsize=10, fontweight='bold')
    ax_f.set_title('Locomotor Frequency', fontsize=10.5, fontweight='bold')
    ax_f.grid(True, linestyle=':', alpha=0.4, axis='y')
    for bar in bars_f:
        yval = bar.get_height()
        ax_f.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, f"{yval:.2f} Hz", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    # 2. Polar Phase Plot showing L-R switch to 0 deg
    ax_p = fig.add_subplot(gs[0, 1], projection='polar')
    for name, m, col in [('Control', control_metrics, '#333333'), ('V0 Ablation', v0_metrics, '#e7298a')]:
        phi_lr = m['lr_phase_rad']
        phi_fe = m['fe_phase_rad']
        ax_p.annotate('', xy=(phi_lr, 0.85), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=2.0))
        ax_p.scatter([phi_lr], [0.85], color=col, s=60, label=f"{name} L-R: {m['lr_phase_deg']:.1f}°")
        ax_p.scatter([phi_fe], [0.55], color=col, marker='s', s=40, label=f"{name} F-E: {m['fe_phase_deg']:.1f}°")

    ax_p.set_title('Phase Coordination\n(Left–Right Alternation $\\to$ Synchrony)', fontsize=10.5, fontweight='bold', pad=12)
    ax_p.set_ylim(0.0, 1.0)
    ax_p.set_yticklabels([])
    ax_p.legend(loc='lower center', bbox_to_anchor=(0.5, -0.4), fontsize=7.5, frameon=True)

    plt.suptitle('Figure 5F: V0 Ablation Quantification', fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def generate_figure5_complete(
    suite_results: Dict[str, Tuple[Any, Dict[str, Any], Any]],
    output_dir: str = "plots",
    dpi: int = 300
) -> Dict[str, str]:
    """
    Generates all individual Figure 5 panels (5A–5F) and the composite summary figure.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}

    ctrl_res, ctrl_m, ctrl_net = suite_results['control']
    v1_res, v1_m, v1_net = suite_results['v1']
    v0_res, v0_m, v0_net = suite_results['v0']

    # 5A
    p5a = os.path.join(output_dir, "13_fig5a_v1_projectome.png")
    fig5a = plot_panel_5a_v1_projectome(ctrl_net, v1_net, p5a, dpi=dpi)
    plt.close(fig5a)
    generated_files['panel_5a'] = p5a

    # 5B
    p5b = os.path.join(output_dir, "14_fig5b_v1_activity_emg.png")
    fig5b = plot_panel_5b_v1_activity_emg(ctrl_res, v1_res, ctrl_net, v1_net, p5b, dpi=dpi)
    plt.close(fig5b)
    generated_files['panel_5b'] = p5b

    # 5C
    p5c = os.path.join(output_dir, "15_fig5c_v1_quantification.png")
    fig5c = plot_panel_5c_v1_quantification(ctrl_m, v1_m, p5c, dpi=dpi)
    plt.close(fig5c)
    generated_files['panel_5c'] = p5c

    # 5D
    p5d = os.path.join(output_dir, "16_fig5d_v0_projectome.png")
    fig5d = plot_panel_5d_v0_projectome(ctrl_net, v0_net, p5d, dpi=dpi)
    plt.close(fig5d)
    generated_files['panel_5d'] = p5d

    # 5E
    p5e = os.path.join(output_dir, "17_fig5e_v0_activity_emg.png")
    fig5e = plot_panel_5e_v0_activity_emg(ctrl_res, v0_res, ctrl_net, v0_net, p5e, dpi=dpi)
    plt.close(fig5e)
    generated_files['panel_5e'] = p5e

    # 5F
    p5f = os.path.join(output_dir, "18_fig5f_v0_quantification.png")
    fig5f = plot_panel_5f_v0_quantification(ctrl_m, v0_m, p5f, dpi=dpi)
    plt.close(fig5f)
    generated_files['panel_5f'] = p5f

    # Composite Figure 5
    fig_comp = plt.figure(figsize=(16, 12), dpi=dpi)
    gs = fig_comp.add_gridspec(2, 3, height_ratios=[1, 1])

    # Top row: V1 perturbation (5A, 5B, 5C)
    # 5A
    ax_a = fig_comp.add_subplot(gs[0, 0])
    dz_c, p_c = compute_projectome_1d_profile(ctrl_net, target_pop='V1')
    dz_v, p_v = compute_projectome_1d_profile(v1_net, target_pop='V1')
    ax_a.plot(dz_c, p_c, color='#377eb8', lw=2, label='Control V1 Lobe')
    ax_a.plot(dz_v, p_v, color='#d95f02', lw=2, linestyle='--', label='V1 Ablated')
    ax_a.set_title('A: V1 Rostral Inhibitory Lobe Deletion', fontweight='bold', fontsize=11)
    ax_a.set_xlabel('$\\Delta Z$ (µm)', fontsize=9)
    ax_a.set_ylabel('Synaptic Weight', fontsize=9)
    ax_a.legend(fontsize=8)
    ax_a.grid(True, linestyle=':', alpha=0.4)

    # 5B
    ax_b = fig_comp.add_subplot(gs[0, 1])
    t_mask = (ctrl_res.time_ms >= 4000) & (ctrl_res.time_ms <= 6000)
    t_s = (ctrl_res.time_ms[t_mask] - 4000) / 1000.0
    ax_b.plot(t_s, ctrl_res.population_rates['MN'][t_mask], color='#333333', lw=1.8, label='Control MN')
    ax_b.plot(t_s, v1_res.population_rates['MN'][t_mask], color='#d95f02', lw=1.8, label='V1 Ablated MN')
    ax_b.set_title('B: Rhythm Deceleration & Disinhibition', fontweight='bold', fontsize=11)
    ax_b.set_xlabel('Time (s)', fontsize=9)
    ax_b.set_ylabel('Rate (Hz)', fontsize=9)
    ax_b.legend(fontsize=8)
    ax_b.grid(True, linestyle=':', alpha=0.4)

    # 5C
    ax_c = fig_comp.add_subplot(gs[0, 2], projection='polar')
    for name, m, col in [('Control', ctrl_m, '#333333'), ('V1 Ablated', v1_m, '#d95f02')]:
        phi = m['lr_phase_rad']
        ax_c.annotate('', xy=(phi, 0.9), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=2))
        ax_c.scatter([phi], [0.9], color=col, s=50, label=f"{name} ({m['lr_phase_deg']:.1f}°)")
    ax_c.set_title('C: Preserved Left–Right Alternation', fontweight='bold', fontsize=11, pad=10)
    ax_c.set_ylim(0, 1.1)
    ax_c.set_yticklabels([])
    ax_c.legend(fontsize=8, loc='lower left')

    # Bottom row: V0 perturbation (5D, 5E, 5F)
    # 5D
    ax_d = fig_comp.add_subplot(gs[1, 0])
    dz_c0, p_c0 = compute_projectome_1d_profile(ctrl_net, contralateral_only=True)
    dz_v0, p_v0 = compute_projectome_1d_profile(v0_net, contralateral_only=True)
    ax_d.plot(dz_c0, p_c0, color='#1b9e77', lw=2, label='Control Contra')
    ax_d.plot(dz_v0, p_v0, color='#e7298a', lw=2, linestyle='--', label='V0 Ablated')
    ax_d.set_title('D: Contralateral Projectome Deletion', fontweight='bold', fontsize=11)
    ax_d.set_xlabel('$\\Delta Z$ (µm)', fontsize=9)
    ax_d.set_ylabel('Contra Weight', fontsize=9)
    ax_d.legend(fontsize=8)
    ax_d.grid(True, linestyle=':', alpha=0.4)

    # 5E
    ax_e = fig_comp.add_subplot(gs[1, 1])
    emg_v0 = generate_synthetic_emg(
        rates=v0_res.rates,
        neuron_types=v0_net.types,
        neuron_lat=v0_net.latera,
        neuron_z=v0_net.pos_z,
        time_ms=v0_res.time_ms,
        noise_level=0.15,
        window_ms=20,
        rng_seed=42
    )
    if 'Left' in emg_v0 and 'Right' in emg_v0 and 'Tibialis Anterior' in emg_v0['Left']['muscles']:
        idx = list(emg_v0['Left']['muscles']).index('Tibialis Anterior')
        ax_e.plot(t_s, emg_v0['Left']['envelope'][t_mask, idx], color='#377eb8', label='L-TA (Flex)', lw=1.8)
        ax_e.plot(t_s, emg_v0['Right']['envelope'][t_mask, idx], color='#e41a1c', label='R-TA (Flex)', lw=1.8, linestyle='--')
    ax_e.set_title('E: Synchronous Bilateral Bursts (Hopping)', fontweight='bold', fontsize=11)
    ax_e.set_xlabel('Time (s)', fontsize=9)
    ax_e.set_ylabel('EMG Envelope', fontsize=9)
    ax_e.legend(fontsize=8)
    ax_e.grid(True, linestyle=':', alpha=0.4)

    # 5F
    ax_f = fig_comp.add_subplot(gs[1, 2], projection='polar')
    for name, m, col in [('Control', ctrl_m, '#333333'), ('V0 Ablated', v0_m, '#e7298a')]:
        phi = m['lr_phase_rad']
        ax_f.annotate('', xy=(phi, 0.9), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=2))
        ax_f.scatter([phi], [0.9], color=col, s=50, label=f"{name} ({m['lr_phase_deg']:.1f}°)")
    ax_f.set_title('F: Alternation $\\to$ Synchrony ($0^\\circ$)', fontweight='bold', fontsize=11, pad=10)
    ax_f.set_ylim(0, 1.1)
    ax_f.set_yticklabels([])
    ax_f.legend(fontsize=8, loc='lower left')

    fig_comp.suptitle('Figure 5: Cell-Type Specific Perturbations in the Mouse Spinal Projectome Model (Komi et al. 2026)', fontsize=14, fontweight='bold', y=0.99)
    plt.tight_layout()

    p_comp = os.path.join(output_dir, "19_figure5_complete.png")
    fig_comp.savefig(p_comp, bbox_inches='tight', dpi=dpi)
    plt.close(fig_comp)
    generated_files['figure5_complete'] = p_comp

    return generated_files
