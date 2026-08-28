"""
Figure 1 Analysis and Visualization Module.
Reproduces Figure 1 from Komi et al. (Nature Communications, 2026):
- Panels 1A-C: Non-spatial BSG random network graph, sequential multi-phase dynamics, PC1-PC2 limit cycle.
- Panels 1D-E: Phase-space unfolded connectivity matrix and emergent 1D asymmetric Mexican-hat projectome.
- Panel 1F: 1D 5-subpopulation spatial kernels and traveling wave raster.
- Panel 1G: sp3 gain modulation -> selective burst amplitude control & PC orbit expansion.
- Panel 1H: sp2 gain modulation -> selective frequency control & preserved orbit radius.
- Unified Composite Figure 1.
"""

import os
from typing import Optional, Dict, Any, List
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

POP_COLORS = {
    'sp1': '#e41a1c',  # Red (Local Excitatory)
    'sp2': '#377eb8',  # Blue (Frequency Inhibitory)
    'sp3': '#4daf4a',  # Green (Amplitude Excitatory)
    'sp4': '#984ea3',  # Purple (Surround Inhibitory)
    'sp5': '#ff7f0e'   # Orange (Long-Range Excitatory)
}


def plot_panel_1abc_bsg_dynamics(
    bsg_net: Any,
    sim_res: Dict[str, np.ndarray],
    unfold_res: Dict[str, Any],
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panels 1A-C: BSG random recurrent network, sequential multi-phase rate trajectories,
    and 2D PCA rotational limit cycle orbit.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14.0, 4.2), dpi=dpi)

    # 1A: Non-spatial Random Recurrent Network Connectivity Heatmap
    W = bsg_net.conn_mat
    vmax = np.percentile(np.abs(W), 99)
    im1 = ax1.imshow(W, cmap='bwr', aspect='auto', vmin=-vmax, vmax=vmax)
    ax1.set_title('1A: Non-Spatial BSG Matrix ($N=500$)', fontsize=10.5, fontweight='bold', pad=8)
    ax1.set_xlabel('Presynaptic Neuron Index', fontsize=9, fontweight='bold')
    ax1.set_ylabel('Postsynaptic Neuron Index', fontsize=9, fontweight='bold')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04, label='Weight ($W_{ij}$)')

    # 1B: Sequential Multi-Neuron Rate Trajectories
    time_ms = sim_res['time_ms']
    t_mask = (time_ms >= 4000) & (time_ms <= 6000)
    t_sec = (time_ms[t_mask] - 4000) / 1000.0

    # Pick 8 neurons sorted by phase
    sort_order = unfold_res['sort_order']
    sample_neurons = sort_order[np.linspace(0, len(sort_order) - 1, 8, dtype=int)]
    colors = plt.cm.turbo(np.linspace(0, 1, 8))

    for idx, (n_idx, col) in enumerate(zip(sample_neurons, colors)):
        rate = sim_res['rates'][t_mask, n_idx]
        ax2.plot(t_sec, rate + idx * 8.0, color=col, lw=1.6, label=f'Neuron {n_idx}' if idx in [0, 7] else None)

    ax2.set_title('1B: Multi-Phase Sequential Firing', fontsize=10.5, fontweight='bold', pad=8)
    ax2.set_xlabel('Time (s)', fontsize=9, fontweight='bold')
    ax2.set_ylabel('Firing Rate + Offset (Hz)', fontsize=9, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.4)
    ax2.legend(loc='upper right', fontsize=7.5, frameon=True)

    # 1C: 2D PCA Rotational Limit Cycle Orbit
    scores = unfold_res['pca_scores']
    t_pca_mask = (len(scores) - 2000)
    ax3.plot(scores[-2000:, 0], scores[-2000:, 1], color='#2b5c8f', lw=1.8, label='Limit Cycle')
    ax3.scatter(scores[-1, 0], scores[-1, 1], color='crimson', s=45, zorder=5, label='End State')
    var_exp = unfold_res['explained_variance_ratio']
    ax3.set_title(f'1C: PCA Limit Cycle Orbit\n(PC1: {var_exp[0]*100:.1f}%, PC2: {var_exp[1]*100:.1f}%)', fontsize=10.5, fontweight='bold', pad=8)
    ax3.set_xlabel('Principal Component 1 (PC1)', fontsize=9, fontweight='bold')
    ax3.set_ylabel('Principal Component 2 (PC2)', fontsize=9, fontweight='bold')
    ax3.grid(True, linestyle=':', alpha=0.4)
    ax3.legend(loc='upper right', fontsize=7.5, frameon=True)

    plt.suptitle('Figure 1A–C: Balanced Sequence Generator (BSG) Random Recurrent Dynamics', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_1de_unfolded_projectome(
    unfold_res: Dict[str, Any],
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panels 1D-E: Phase-space unfolded 1D sorted connectivity matrix and emergent
    asymmetric Mexican-hat projectome profile.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.5), dpi=dpi, gridspec_kw={'width_ratios': [1.1, 1]})

    # 1D: Unfolded Permuted Connectivity Matrix Heatmap
    W_unfolded = unfold_res['W_unfolded']
    vmax = np.percentile(np.abs(W_unfolded), 99)
    im1 = ax1.imshow(W_unfolded, cmap='bwr', aspect='auto', vmin=-vmax, vmax=vmax)
    ax1.set_title(r'1D: Phase-Unfolded Matrix $W_{\Pi,\Pi}$', fontsize=10.5, fontweight='bold', pad=8)
    ax1.set_xlabel(r'Sorted Presynaptic ($\theta \rightarrow 2\pi$)', fontsize=9, fontweight='bold')
    ax1.set_ylabel(r'Sorted Postsynaptic ($\theta \rightarrow 2\pi$)', fontsize=9, fontweight='bold')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04, label='Weight ($W_{ij}$)')

    # 1E: Emergent 1D Mexican-Hat Projectome Profile
    d_theta = unfold_res['delta_theta_centers']
    prof = unfold_res['projectome_profile']
    prof_e = unfold_res['projectome_excit']
    prof_i = unfold_res['projectome_inhib']

    ax2.plot(d_theta, prof, color='#111111', lw=2.2, label='Net Projectome (E - I)')
    ax2.fill_between(d_theta, 0, prof_e, color='#e41a1c', alpha=0.3, label='Excitatory Cloud')
    ax2.fill_between(d_theta, 0, prof_i, color='#377eb8', alpha=0.3, label='Inhibitory Surround')
    ax2.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax2.axvline(0, color='gray', linestyle=':', lw=1.0)

    ax2.set_title('1E: Emergent Asymmetric Mexican-Hat', fontsize=10.5, fontweight='bold', pad=8)
    ax2.set_xlabel('Phase Distance $\\Delta \\theta = \\theta_i - \\theta_j$ (rad)', fontsize=9, fontweight='bold')
    ax2.set_ylabel('Average Synaptic Weight', fontsize=9, fontweight='bold')
    ax2.set_xlim(-np.pi, np.pi)
    ax2.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
    ax2.set_xticklabels(['$-\\pi$', '$-\\pi/2$', '$0$', '$\\pi/2$', '$\\pi$'])
    ax2.grid(True, linestyle=':', alpha=0.4)
    ax2.legend(loc='upper right', fontsize=8, frameon=True)

    plt.suptitle('Figure 1D–E: Phase Unfolding of Non-Spatial BSG into Asymmetric Mexican Hat', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_1f_5pop_network(
    net_1d: Any,
    sim_res: Dict[str, np.ndarray],
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 1F: 1D 5-Subpopulation Mexican-hat spatial kernels and traveling wave raster.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5), dpi=dpi, gridspec_kw={'width_ratios': [1, 1.2]})

    # 1. Spatial Kernel Profiles
    dz = np.linspace(-2500, 2500, 500)
    for pop in net_1d.pop_configs:
        sign = 1.0 if pop.is_excitatory else -1.0
        k_val = sign * np.exp(-((dz - pop.mu_um)**2) / (2.0 * pop.sigma_um**2))
        ax1.plot(dz, k_val, color=POP_COLORS.get(pop.name, '#333333'), lw=2.0, label=f"{pop.name} ({'+' if pop.is_excitatory else '-'}, $\\mu={int(pop.mu_um)}\\mu$m)")

    ax1.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax1.axvline(0, color='gray', linestyle=':', lw=1.0)
    ax1.set_title('1F: 5-Subpopulation Spatial Kernels ($sp_1-sp_5$)', fontsize=10.5, fontweight='bold', pad=8)
    ax1.set_xlabel('Spatial Distance $\\Delta Z$ (µm)', fontsize=9, fontweight='bold')
    ax1.set_ylabel('Synaptic Weight Kernel', fontsize=9, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.4)
    ax1.legend(loc='upper right', fontsize=7.5, frameon=True)

    # 2. Spatiotemporal Traveling Wave Raster
    time_ms = sim_res['time_ms']
    t_mask = (time_ms >= 4000) & (time_ms <= 6000)
    t_sec = (time_ms[t_mask] - 4000) / 1000.0
    r_sorted = sim_res['rates'][t_mask, :].T

    im2 = ax2.imshow(r_sorted, aspect='auto', cmap='magma', extent=[0, 2.0, 0, net_1d.length_um], origin='lower')
    ax2.set_title('Spatiotemporal Traveling Wave Along 1D Line', fontsize=10.5, fontweight='bold', pad=8)
    ax2.set_xlabel('Time (s)', fontsize=9, fontweight='bold')
    ax2.set_ylabel('Longitudinal Position $Z$ (µm)', fontsize=9, fontweight='bold')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, label='Firing Rate (Hz)')

    plt.suptitle('Figure 1F: 1D 5-Subpopulation Mexican-Hat Network Model', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_1g_amplitude_control(
    sweep_data: Dict[str, Any],
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 1G: Subpopulation sp3 gain modulation selectively controls burst amplitude
    and expands PC1-PC2 limit cycle orbit without changing oscillation frequency.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14.0, 4.2), dpi=dpi)

    gains = sweep_data['gain_levels']
    freqs = sweep_data['frequencies_hz']
    amps = sweep_data['amplitudes_hz']
    runs = sweep_data['sim_runs']

    # 1. Overlay Firing Rate Traces
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(gains)))

    for i, g in enumerate(gains):
        run = runs[f"gain_{g:.2f}"]
        # Pick representative neuron
        sample_trace = run['sample_rates'][:, 0]
        t_sec = np.linspace(0, len(sample_trace) / 1000.0, len(sample_trace))
        ax1.plot(t_sec, sample_trace, color=colors[i], lw=1.8, label=f"$g_3 = {g:.2f}$")

    ax1.set_title('1G: $sp_3$ Gain Modulates Burst Amplitude', fontsize=10.5, fontweight='bold', pad=8)
    ax1.set_xlabel('Time (s)', fontsize=9, fontweight='bold')
    ax1.set_ylabel('Neuron Firing Rate (Hz)', fontsize=9, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.4)
    ax1.legend(loc='upper right', fontsize=7.5, frameon=True)

    # 2. PCA Phase-Space Orbit Expansion
    for i, g in enumerate(gains):
        run = runs[f"gain_{g:.2f}"]
        n_pts = min(1500, len(run['pca_scores']))
        sc = run['pca_scores'][-n_pts:, :]
        ax2.plot(sc[:, 0], sc[:, 1], color=colors[i], lw=1.6, label=f"$g_3 = {g:.2f}$")

    ax2.set_title('PCA Orbit Expansion ($R_{\\text{orbit}} \\uparrow$)', fontsize=10.5, fontweight='bold', pad=8)
    ax2.set_xlabel('PC1', fontsize=9, fontweight='bold')
    ax2.set_ylabel('PC2', fontsize=9, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.4)
    ax2.legend(loc='upper right', fontsize=7.5, frameon=True)

    # 3. Quantification: Amplitude vs Frequency Curves
    ax3_twin = ax3.twinx()
    l1 = ax3.plot(gains, amps, color='#2ca02c', marker='o', lw=2.2, label='Amplitude (Hz)')
    l2 = ax3_twin.plot(gains, freqs, color='#d62728', marker='s', linestyle='--', lw=2.0, label='Frequency (Hz)')

    ax3.set_xlabel('$sp_3$ Excitatory Gain $g_3$', fontsize=9, fontweight='bold')
    ax3.set_ylabel('Burst Amplitude (RMS, Hz)', color='#2ca02c', fontsize=9, fontweight='bold')
    ax3_twin.set_ylabel('Frequency (Hz)', color='#d62728', fontsize=9, fontweight='bold')
    ax3.set_title('Decoupled Amplitude Control', fontsize=10.5, fontweight='bold', pad=8)
    ax3.grid(True, linestyle=':', alpha=0.4)

    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc='upper left', fontsize=7.5, frameon=True)

    plt.suptitle('Figure 1G: Selective Amplitude Control via Long-Range Excitatory $sp_3$ Gain Modulation', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_1h_frequency_control(
    sweep_data: Dict[str, Any],
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 1H: Subpopulation sp2 gain modulation selectively controls oscillation frequency (speed)
    while preserving limit cycle orbit radius and burst amplitude.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14.0, 4.2), dpi=dpi)

    gains = sweep_data['gain_levels']
    freqs = sweep_data['frequencies_hz']
    amps = sweep_data['amplitudes_hz']
    runs = sweep_data['sim_runs']

    # 1. Overlay Firing Rate Traces
    colors = plt.cm.coolwarm(np.linspace(0.1, 0.9, len(gains)))

    for i, g in enumerate(gains):
        run = runs[f"gain_{g:.2f}"]
        sample_trace = run['sample_rates'][:, 0]
        t_sec = np.linspace(0, len(sample_trace) / 1000.0, len(sample_trace))
        ax1.plot(t_sec, sample_trace, color=colors[i], lw=1.8, label=f"$g_2 = {g:.2f}$")

    ax1.set_title('1H: $sp_2$ Gain Modulates Locomotor Frequency', fontsize=10.5, fontweight='bold', pad=8)
    ax1.set_xlabel('Time (s)', fontsize=9, fontweight='bold')
    ax1.set_ylabel('Neuron Firing Rate (Hz)', fontsize=9, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.4)
    ax1.legend(loc='upper right', fontsize=7.5, frameon=True)

    # 2. PCA Phase-Space Orbit Invariance
    for i, g in enumerate(gains):
        run = runs[f"gain_{g:.2f}"]
        n_pts = min(1500, len(run['pca_scores']))
        sc = run['pca_scores'][-n_pts:, :]
        ax2.plot(sc[:, 0], sc[:, 1], color=colors[i], lw=1.6, label=f"$g_2 = {g:.2f}$")

    ax2.set_title('Preserved Limit Cycle Orbit Radius', fontsize=10.5, fontweight='bold', pad=8)
    ax2.set_xlabel('PC1', fontsize=9, fontweight='bold')
    ax2.set_ylabel('PC2', fontsize=9, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.4)
    ax2.legend(loc='upper right', fontsize=7.5, frameon=True)

    # 3. Quantification: Frequency vs Amplitude Curves
    ax3_twin = ax3.twinx()
    l1 = ax3.plot(gains, freqs, color='#1f77b4', marker='s', lw=2.2, label='Frequency (Hz)')
    l2 = ax3_twin.plot(gains, amps, color='#2ca02c', marker='o', linestyle='--', lw=2.0, label='Amplitude (Hz)')

    ax3.set_xlabel('$sp_2$ Inhibitory Gain $g_2$', fontsize=9, fontweight='bold')
    ax3.set_ylabel('Locomotor Frequency (Hz)', color='#1f77b4', fontsize=9, fontweight='bold')
    ax3_twin.set_ylabel('Burst Amplitude (RMS, Hz)', color='#2ca02c', fontsize=9, fontweight='bold')
    ax3.set_title('Decoupled Frequency Control', fontsize=10.5, fontweight='bold', pad=8)
    ax3.grid(True, linestyle=':', alpha=0.4)

    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc='upper left', fontsize=7.5, frameon=True)

    plt.suptitle('Figure 1H: Selective Frequency Control via Inhibitory $sp_2$ Gain Modulation', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_figure1_complete(
    bsg_data: Dict[str, Any],
    model1d_data: Dict[str, Any],
    sp3_sweep: Dict[str, Any],
    sp2_sweep: Dict[str, Any],
    output_path: str = "plots/figure1_complete.png",
    dpi: int = 300
) -> plt.Figure:
    """
    Unified composite Figure 1 matching Nature Communications layout:
      Top Row: 1A-B (BSG dynamics), 1D (Unfolded Matrix), 1E (Mexican Hat).
      Bottom Row: 1F (5-Pop Kernels/Raster), 1G (sp3 Amplitude control), 1H (sp2 Frequency control).
    """
    fig = plt.figure(figsize=(18, 11), dpi=dpi)
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1])

    # Top Left: 1A BSG Dynamics & Limit Cycle
    ax_a = fig.add_subplot(gs[0, 0])
    scores = bsg_data['unfold_res']['pca_scores']
    ax_a.plot(scores[-2000:, 0], scores[-2000:, 1], color='#2b5c8f', lw=1.8, label='Orbit')
    ax_a.scatter(scores[-1, 0], scores[-1, 1], color='crimson', s=40, zorder=5)
    ax_a.set_title('A–C: BSG Phase-Space Limit Cycle ($N=500$)', fontweight='bold', fontsize=11)
    ax_a.set_xlabel('PC1', fontsize=9)
    ax_a.set_ylabel('PC2', fontsize=9)
    ax_a.grid(True, linestyle=':', alpha=0.4)

    # Top Middle: 1D Unfolded Matrix
    ax_d = fig.add_subplot(gs[0, 1])
    W_unfolded = bsg_data['unfold_res']['W_unfolded']
    vmax = np.percentile(np.abs(W_unfolded), 99)
    im_d = ax_d.imshow(W_unfolded, cmap='bwr', aspect='auto', vmin=-vmax, vmax=vmax)
    ax_d.set_title(r'D: Phase-Unfolded Matrix $W_{\Pi,\Pi}$', fontweight='bold', fontsize=11)
    ax_d.set_xlabel(r'Sorted Presynaptic ($\theta \rightarrow 2\pi$)', fontsize=9)
    ax_d.set_ylabel(r'Sorted Postsynaptic ($\theta \rightarrow 2\pi$)', fontsize=9)
    plt.colorbar(im_d, ax=ax_d, fraction=0.046, pad=0.04)

    # Top Right: 1E Emergent Mexican-Hat
    ax_e = fig.add_subplot(gs[0, 2])
    d_theta = bsg_data['unfold_res']['delta_theta_centers']
    prof = bsg_data['unfold_res']['projectome_profile']
    prof_e = bsg_data['unfold_res']['projectome_excit']
    prof_i = bsg_data['unfold_res']['projectome_inhib']
    ax_e.plot(d_theta, prof, color='#111111', lw=2.2, label='Net Projectome')
    ax_e.fill_between(d_theta, 0, prof_e, color='#e41a1c', alpha=0.3, label='Excitatory')
    ax_e.fill_between(d_theta, 0, prof_i, color='#377eb8', alpha=0.3, label='Inhibitory')
    ax_e.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax_e.set_title('E: Emergent 1D Asymmetric Mexican Hat', fontweight='bold', fontsize=11)
    ax_e.set_xlabel('Phase Distance $\\Delta \\theta$ (rad)', fontsize=9)
    ax_e.set_ylabel('Average Weight', fontsize=9)
    ax_e.set_xlim(-np.pi, np.pi)
    ax_e.set_xticks([-np.pi, 0, np.pi])
    ax_e.set_xticklabels(['$-\\pi$', '$0$', '$\\pi$'])
    ax_e.legend(fontsize=8, loc='upper right')
    ax_e.grid(True, linestyle=':', alpha=0.4)

    # Bottom Left: 1F 1D 5-Subpopulation Traveling Wave
    ax_f = fig.add_subplot(gs[1, 0])
    time_ms = model1d_data['sim_res']['time_ms']
    t_mask = (time_ms >= 4000) & (time_ms <= 6000)
    r_sorted = model1d_data['sim_res']['rates'][t_mask, :].T
    im_f = ax_f.imshow(r_sorted, aspect='auto', cmap='magma', extent=[0, 2.0, 0, model1d_data['net_1d'].length_um], origin='lower')
    ax_f.set_title('F: 1D 5-Subpopulation Traveling Wave', fontweight='bold', fontsize=11)
    ax_f.set_xlabel('Time (s)', fontsize=9)
    ax_f.set_ylabel('Longitudinal $Z$ (µm)', fontsize=9)
    plt.colorbar(im_f, ax=ax_f, fraction=0.046, pad=0.04)

    # Bottom Middle: 1G sp3 Amplitude Gain Modulation
    ax_g = fig.add_subplot(gs[1, 1])
    ax_g_twin = ax_g.twinx()
    l1 = ax_g.plot(sp3_sweep['gain_levels'], sp3_sweep['amplitudes_hz'], color='#2ca02c', marker='o', lw=2.2, label='Amplitude')
    l2 = ax_g_twin.plot(sp3_sweep['gain_levels'], sp3_sweep['frequencies_hz'], color='#d62728', marker='s', linestyle='--', lw=2.0, label='Frequency')
    ax_g.set_title('G: $sp_3$ Gain Controls Amplitude', fontweight='bold', fontsize=11)
    ax_g.set_xlabel('$sp_3$ Excitatory Gain $g_3$', fontsize=9)
    ax_g.set_ylabel('Amplitude (RMS, Hz)', color='#2ca02c', fontsize=9)
    ax_g_twin.set_ylabel('Frequency (Hz)', color='#d62728', fontsize=9)
    ax_g.grid(True, linestyle=':', alpha=0.4)

    # Bottom Right: 1H sp2 Frequency Gain Modulation
    ax_h = fig.add_subplot(gs[1, 2])
    ax_h_twin = ax_h.twinx()
    l3 = ax_h.plot(sp2_sweep['gain_levels'], sp2_sweep['frequencies_hz'], color='#1f77b4', marker='s', lw=2.2, label='Frequency')
    l4 = ax_h_twin.plot(sp2_sweep['gain_levels'], sp2_sweep['amplitudes_hz'], color='#2ca02c', marker='o', linestyle='--', lw=2.0, label='Amplitude')
    ax_h.set_title('H: $sp_2$ Gain Controls Frequency', fontweight='bold', fontsize=11)
    ax_h.set_xlabel('$sp_2$ Inhibitory Gain $g_2$', fontsize=9)
    ax_h.set_ylabel('Frequency (Hz)', color='#1f77b4', fontsize=9)
    ax_h_twin.set_ylabel('Amplitude (RMS, Hz)', color='#2ca02c', fontsize=9)
    ax_h.grid(True, linestyle=':', alpha=0.4)

    fig.suptitle('Figure 1: Balanced Sequence Generation, Mexican-Hat Projectomes, and Decoupled Motor Control', fontsize=14, fontweight='bold', y=0.99)
    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
        # Also save 00_figure1_complete.png alias if helpful
        alt_path = os.path.join(os.path.dirname(output_path), "00_figure1_complete.png")
        fig.savefig(alt_path, bbox_inches='tight', dpi=dpi)

    return fig
