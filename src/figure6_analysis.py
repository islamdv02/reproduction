"""
Figure 6 Publication-Quality Multi-Panel Generator:
Spinal Cord Lesion, Targeted Axonal Regrowth, and High-Density Electrophysiology.

Faithfully reproduces and analyzes Figure 6 from Komi et al., Nature Communications, 2026:
- 6A: Anatomical lesion at L2/L3 boundary and projectome disruption (severed long-range tails)
- 6B: Spatiotemporal locomotor dynamics post-lesion (traveling wave arrest caudal to lesion)
- 6C: Cell-type specific axonal regrowth comparison (V2a-2 vs V1 vs V0v vs V3)
- 6D: Functional recovery of locomotor rhythm & EMG under targeted V2a-2 regrowth
- 6E: High-density 32-channel silicon probe virtual insertion in 3D lumbar cord
- 6F: Multi-channel spike rasters, smoothed rate heatmaps, and depth-dependent phase progression
- Composite Figure 6: Unified 6-panel publication composite
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, Optional, Tuple, List

from locomotion import generate_synthetic_emg, MUSCLE_FLEX_EXT
from figure3_analysis import POP_COLORS, MUSCLE_COLORS
from figure5_analysis import compute_projectome_1d_profile
from electrophysiology import VirtualProbe, ProbeConfig, generate_poisson_spikes, estimate_instantaneous_rates, compute_channel_phase_lags


def plot_panel_6a_lesion_projectome(
    control_net: Any,
    lesioned_net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 6A: Anatomical transverse lesion and projectome profile disruption.
    Demonstrates that severing cross-boundary connections truncates long-range projection tails.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=dpi, gridspec_kw={'width_ratios': [1.1, 1.2]})

    # Left: 3D soma distribution with lesion plane
    z_lesion = getattr(lesioned_net, 'z_lesion_um', 4000.0)
    pos_x = control_net.pos_x
    pos_z = control_net.pos_z
    types = control_net.types

    for pop in np.unique(types):
        p_mask = (types == pop)
        col = POP_COLORS.get(str(pop), '#888888')
        ax1.scatter(pos_z[p_mask], pos_x[p_mask], s=8, color=col, alpha=0.45, edgecolors='none', label=str(pop))

    ax1.axvline(z_lesion, color='#e41a1c', linestyle='--', lw=2.5, label=f'Lesion Plane ($Z={z_lesion:.0f}$ µm)')
    ax1.set_xlabel('Rostrocaudal Position $Z$ (µm)\n(Rostral $T_{13} \\rightarrow$ Caudal $S_4$)', fontsize=9.5, fontweight='bold')
    ax1.set_ylabel('Mediolateral Position $X$ (µm)', fontsize=9.5, fontweight='bold')
    ax1.set_title('Transverse Spinal Cord Lesion ($L_2/L_3$)', fontsize=10.5, fontweight='bold', pad=8)
    ax1.grid(True, linestyle=':', alpha=0.4)
    ax1.legend(loc='upper right', fontsize=6.5, ncol=2, frameon=True)

    # Right: 1D projectome comparison before vs after lesion
    dz_ctrl, prof_ctrl = compute_projectome_1d_profile(control_net, max_dist_um=5000.0)
    dz_les, prof_les = compute_projectome_1d_profile(lesioned_net, max_dist_um=5000.0)

    ax2.plot(dz_ctrl, prof_ctrl, color='#333333', lw=2.2, label='Intact Control Projectome')
    ax2.plot(dz_les, prof_les, color='#e41a1c', lw=2.2, linestyle='--', label='Post-Lesion Projectome')
    ax2.fill_between(dz_ctrl, prof_ctrl, prof_les, color='#e41a1c', alpha=0.2, label='Severed Synaptic Efficacy')

    ax2.axvline(0, color='#888888', linestyle=':', alpha=0.7)
    ax2.axhline(0, color='#888888', linestyle='-', alpha=0.5)
    ax2.set_xlabel('Rostrocaudal Distance $\\Delta Z$ (µm)', fontsize=9.5, fontweight='bold')
    ax2.set_ylabel('Net Synaptic Weight (a.u.)', fontsize=9.5, fontweight='bold')
    ax2.set_title('Projectome Disruption: Severed Long-Range Tails', fontsize=10.5, fontweight='bold', pad=8)
    ax2.grid(True, linestyle=':', alpha=0.4)
    ax2.legend(loc='upper right', fontsize=8.5, frameon=True)

    plt.suptitle('Figure 6A: Structural Lesion at $L_2/L_3$ Breaks Longitudinal Mexican-Hat Kernel', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_6b_post_lesion_dynamics(
    control_res: Any,
    lesion_res: Any,
    control_net: Any,
    lesion_net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 6B: Spatiotemporal traveling wave arrest and EMG breakdown post-lesion.
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 8), dpi=dpi, sharex=True)

    t_mask = (control_res.time_ms >= 4000) & (control_res.time_ms <= 6000)
    t_sec = (control_res.time_ms[t_mask] - 4000) / 1000.0

    # Sort neurons by rostrocaudal Z coordinate
    sort_idx = np.argsort(control_net.pos_z)

    # 1. Control Spatiotemporal Heatmap
    r_ctrl_sorted = control_res.rates[t_mask, :][:, sort_idx].T
    im1 = ax1.imshow(r_ctrl_sorted, aspect='auto', cmap='magma', extent=[0, 2.0, 0, control_net.n_neurons], origin='lower')
    ax1.set_title('Control: Propagating Rostrocaudal Traveling Wave', fontsize=10.5, fontweight='bold', pad=6)
    ax1.set_ylabel('Neuron Index ($T_{13} \\rightarrow S_4$)', fontsize=9.5, fontweight='bold')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04, label='Rate (Hz)')

    # 2. Lesioned Spatiotemporal Heatmap
    r_les_sorted = lesion_res.rates[t_mask, :][:, sort_idx].T
    im2 = ax2.imshow(r_les_sorted, aspect='auto', cmap='magma', extent=[0, 2.0, 0, lesion_net.n_neurons], origin='lower')
    ax2.set_title('Post-Lesion: Wave Arrest & Caudal Quiescence', fontsize=10.5, fontweight='bold', pad=6)
    ax2.set_ylabel('Neuron Index ($T_{13} \\rightarrow S_4$)', fontsize=9.5, fontweight='bold')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, label='Rate (Hz)')

    # Synthetic EMG traces
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

    emg_les = generate_synthetic_emg(
        rates=lesion_res.rates,
        neuron_types=lesion_net.types,
        neuron_lat=lesion_net.latera,
        neuron_z=lesion_net.pos_z,
        time_ms=lesion_res.time_ms,
        noise_level=0.15,
        window_ms=20,
        rng_seed=42
    )

    # 3. Control EMG
    offset = 0.0
    for side in ['Left', 'Right']:
        for m_name in ['Tibialis Anterior', 'Gastrocnemius']:
            if side in emg_ctrl and m_name in emg_ctrl[side]['muscles']:
                idx = list(emg_ctrl[side]['muscles']).index(m_name)
                env = emg_ctrl[side]['envelope'][t_mask, idx]
                col = MUSCLE_COLORS['Flex'] if 'Tibialis' in m_name else MUSCLE_COLORS['Ext']
                ls = '-' if side == 'Left' else '--'
                ax3.plot(t_sec, env + offset, color=col, linestyle=ls, lw=1.8, label=f"{side[0]} {m_name}")
                offset += 1.0
    ax3.set_title('Control EMG: Alternating Flexor-Extensor Coordination', fontsize=10.5, fontweight='bold', pad=6)
    ax3.set_xlabel('Time (s)', fontsize=9.5, fontweight='bold')
    ax3.set_ylabel('EMG Envelope (a.u.)', fontsize=9.5, fontweight='bold')
    ax3.set_yticks([])
    ax3.grid(True, linestyle=':', alpha=0.4)
    ax3.legend(loc='upper right', fontsize=7.5, ncol=2, frameon=True)

    # 4. Lesion EMG
    offset = 0.0
    for side in ['Left', 'Right']:
        for m_name in ['Tibialis Anterior', 'Gastrocnemius']:
            if side in emg_les and m_name in emg_les[side]['muscles']:
                idx = list(emg_les[side]['muscles']).index(m_name)
                env = emg_les[side]['envelope'][t_mask, idx]
                col = MUSCLE_COLORS['Flex'] if 'Tibialis' in m_name else MUSCLE_COLORS['Ext']
                ls = '-' if side == 'Left' else '--'
                ax4.plot(t_sec, env + offset, color=col, linestyle=ls, lw=1.8)
                offset += 1.0
    ax4.set_title('Post-Lesion EMG: Collapse of Alternating Motor Bursts', fontsize=10.5, fontweight='bold', pad=6)
    ax4.set_xlabel('Time (s)', fontsize=9.5, fontweight='bold')
    ax4.set_ylabel('EMG Envelope (a.u.)', fontsize=9.5, fontweight='bold')
    ax4.set_yticks([])
    ax4.grid(True, linestyle=':', alpha=0.4)

    plt.suptitle('Figure 6B: Transverse Lesion Arrests Rhythmic Motor Output Caudal to Injury', fontsize=12.5, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_6c_regrowth_comparison(
    control_net: Any,
    lesioned_net: Any,
    regrowth_nets: Dict[str, Any],
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 6C: Comparison of structural reinnervation and projectome profile
    across candidate cell types (V2a-2 vs V1 vs V0v vs V3).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=dpi)

    # 1. Projectome profiles
    dz_ctrl, p_ctrl = compute_projectome_1d_profile(control_net, max_dist_um=4500.0)
    dz_les, p_les = compute_projectome_1d_profile(lesioned_net, max_dist_um=4500.0)

    ax1.plot(dz_ctrl, p_ctrl, color='#333333', lw=2.0, label='Intact Control')
    ax1.plot(dz_les, p_les, color='#e41a1c', lw=1.8, linestyle=':', label='Lesioned Baseline')

    colors_reg = {'V2a-2': '#2ca02c', 'V1': '#1f77b4', 'V0v': '#9467bd', 'V3': '#ff7f0e'}
    for pop, reg_net in regrowth_nets.items():
        clean_pop = pop.replace('regrowth_', '')
        dz_r, p_r = compute_projectome_1d_profile(reg_net, max_dist_um=4500.0)
        col = colors_reg.get(clean_pop, '#888888')
        ax1.plot(dz_r, p_r, color=col, lw=2.2, label=f'Regrowth: {clean_pop}')

    ax1.axvline(0, color='#888888', linestyle=':', alpha=0.7)
    ax1.axhline(0, color='#888888', linestyle='-', alpha=0.5)
    ax1.set_xlabel('Rostrocaudal Distance $\\Delta Z$ (µm)', fontsize=9.5, fontweight='bold')
    ax1.set_ylabel('Net Projectome Synaptic Weight (a.u.)', fontsize=9.5, fontweight='bold')
    ax1.set_title('Reconstituted Projectome Profiles', fontsize=10.5, fontweight='bold', pad=8)
    ax1.grid(True, linestyle=':', alpha=0.4)
    ax1.legend(loc='upper right', fontsize=8, frameon=True)

    # 2. Number of Restored Synapses per Cell Type Bar Chart
    pop_names = [p.replace('regrowth_', '') for p in regrowth_nets.keys()]
    n_restored = [getattr(net, 'n_restored_synapses', 0) for net in regrowth_nets.values()]
    bar_cols = [colors_reg.get(p, '#888888') for p in pop_names]

    bars = ax2.bar(pop_names, n_restored, color=bar_cols, width=0.55, edgecolor='black', lw=1.0)
    ax2.set_ylabel('Number of Restored Synapses Across Lesion', fontsize=9.5, fontweight='bold')
    ax2.set_title('Axonal Reinnervation Capacity Across Lesion Gap', fontsize=10.5, fontweight='bold', pad=8)
    ax2.grid(True, linestyle=':', alpha=0.4, axis='y')

    for bar in bars:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + max(n_restored)*0.02, f"{int(yval):,}", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    plt.suptitle('Figure 6C: Targeted Axonal Regrowth of Genetically Defined Cell Types', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_6d_functional_recovery(
    control_res: Any,
    lesion_res: Any,
    regrowth_results: Dict[str, Tuple[Any, Dict[str, Any], Any]],
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 6D: Functional recovery of locomotor traveling waves & EMG under V2a-2 regrowth vs V1/V0v.
    """
    fig = plt.figure(figsize=(13, 7.5), dpi=dpi)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1])

    t_mask = (control_res.time_ms >= 4000) & (control_res.time_ms <= 6000)
    t_sec = (control_res.time_ms[t_mask] - 4000) / 1000.0

    # 1. Top Left: V2a-2 Regrowth Spatiotemporal Raster
    if 'regrowth_V2a-2' in regrowth_results:
        v2a_res, v2a_m, v2a_net = regrowth_results['regrowth_V2a-2']
    else:
        v2a_res, v2a_m, v2a_net = control_res, {}, list(regrowth_results.values())[0][2]

    sort_idx = np.argsort(v2a_net.pos_z)
    r_v2a_sorted = v2a_res.rates[t_mask, :][:, sort_idx].T

    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.imshow(r_v2a_sorted, aspect='auto', cmap='magma', extent=[0, 2.0, 0, v2a_net.n_neurons], origin='lower')
    ax1.set_title('V2a-2 Regrowth: Rescued Rostrocaudal Traveling Wave', fontsize=10.5, fontweight='bold', pad=6)
    ax1.set_ylabel('Neuron Index ($T_{13} \\rightarrow S_4$)', fontsize=9.5, fontweight='bold')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04, label='Rate (Hz)')

    # 2. Bottom Left: Rescued Synthetic EMG under V2a-2
    emg_v2a = generate_synthetic_emg(
        rates=v2a_res.rates,
        neuron_types=v2a_net.types,
        neuron_lat=v2a_net.latera,
        neuron_z=v2a_net.pos_z,
        time_ms=v2a_res.time_ms,
        noise_level=0.15,
        window_ms=20,
        rng_seed=42
    )

    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
    offset = 0.0
    for side in ['Left', 'Right']:
        for m_name in ['Tibialis Anterior', 'Gastrocnemius']:
            if side in emg_v2a and m_name in emg_v2a[side]['muscles']:
                idx = list(emg_v2a[side]['muscles']).index(m_name)
                env = emg_v2a[side]['envelope'][t_mask, idx]
                col = MUSCLE_COLORS['Flex'] if 'Tibialis' in m_name else MUSCLE_COLORS['Ext']
                ls = '-' if side == 'Left' else '--'
                ax2.plot(t_sec, env + offset, color=col, linestyle=ls, lw=1.8, label=f"{side[0]} {m_name}")
                offset += 1.0
    ax2.set_title('V2a-2 Regrowth EMG: Restored Bilateral Alternation', fontsize=10.5, fontweight='bold', pad=6)
    ax2.set_xlabel('Time (s)', fontsize=9.5, fontweight='bold')
    ax2.set_ylabel('EMG Envelope', fontsize=9.5, fontweight='bold')
    ax2.set_yticks([])
    ax2.grid(True, linestyle=':', alpha=0.4)
    ax2.legend(loc='upper right', fontsize=7.5, ncol=2, frameon=True)

    # 3. Top Right: Frequency Recovery Bar Chart
    ax3 = fig.add_subplot(gs[0, 1])
    cond_labels = ['Control', 'Lesion'] + [k.replace('regrowth_', '') for k in regrowth_results.keys()]
    freqs = [
        float(control_res.spectral_analysis.get('dominant_frequency_hz', 2.5)),
        float(lesion_res.spectral_analysis.get('dominant_frequency_hz', 0.0))
    ] + [m.get('frequency_hz', 0.0) for _, m, _ in regrowth_results.values()]

    cols = ['#333333', '#e41a1c', '#2ca02c', '#1f77b4', '#9467bd', '#ff7f0e'][:len(cond_labels)]
    bars3 = ax3.bar(cond_labels, freqs, color=cols, width=0.55, edgecolor='black', lw=1.0)
    ax3.set_ylabel('Frequency (Hz)', fontsize=9.5, fontweight='bold')
    ax3.set_title('Locomotor Frequency Recovery', fontsize=10.5, fontweight='bold', pad=6)
    ax3.grid(True, linestyle=':', alpha=0.4, axis='y')
    for bar in bars3:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 0.04, f"{yval:.2f}", ha='center', va='bottom', fontsize=8, fontweight='bold')

    # 4. Bottom Right: Motor Burst RMS Amplitude Recovery Bar Chart
    ax4 = fig.add_subplot(gs[1, 1])
    amp_ctrl = float(np.mean(np.sqrt(np.mean((control_res.rates[2000:] - np.mean(control_res.rates[2000:], axis=0))**2, axis=0))))
    amp_les = float(np.mean(np.sqrt(np.mean((lesion_res.rates[2000:] - np.mean(lesion_res.rates[2000:], axis=0))**2, axis=0))))
    amps = [amp_ctrl, amp_les] + [m.get('rms_amplitude_hz', 0.0) for _, m, _ in regrowth_results.values()]

    bars4 = ax4.bar(cond_labels, amps, color=cols, width=0.55, edgecolor='black', lw=1.0)
    ax4.set_ylabel('RMS Rate Amplitude (Hz)', fontsize=9.5, fontweight='bold')
    ax4.set_title('Burst Amplitude Recovery Across Paradigms', fontsize=10.5, fontweight='bold', pad=6)
    ax4.grid(True, linestyle=':', alpha=0.4, axis='y')
    for bar in bars4:
        yval = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2.0, yval + max(amps)*0.02, f"{yval:.3f}", ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.suptitle('Figure 6D: Selective Rescue of Locomotion by V2a-2 Axonal Regrowth', fontsize=12.5, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_6e_probe_insertion(
    network: Any,
    probe: VirtualProbe,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 6E: High-density 32-channel silicon probe virtual insertion in 3D lumbar cord.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=dpi, gridspec_kw={'width_ratios': [1.2, 1]})

    # 1. Transverse cross-section (X, Y) with probe shank and detected units
    pos_x = network.pos_x
    pos_y = network.pos_y
    ch_pos = probe.channel_positions_um

    ax1.scatter(pos_x, pos_y, s=6, color='#bbbbbb', alpha=0.3, label='Spinal Neurons')
    
    # Plot probe shank
    ax1.plot(ch_pos[:, 0], ch_pos[:, 1], color='#333333', lw=3.0, label='Probe Shank (32-ch)')
    sc = ax1.scatter(ch_pos[:, 0], ch_pos[:, 1], c=np.arange(probe.config.n_channels), cmap='viridis', s=45, zorder=4, edgecolor='black')

    # Detected units
    if probe.n_detected_units > 0:
        det_x = pos_x[probe.detected_neuron_indices]
        det_y = pos_y[probe.detected_neuron_indices]
        ax1.scatter(det_x, det_y, c=probe.channel_assignments, cmap='viridis', s=35, marker='o', alpha=0.9, edgecolor='red', lw=0.8, label=f'Detected Units ($n={probe.n_detected_units}$)')

    ax1.set_xlabel('Mediolateral Position $X$ (µm)', fontsize=9.5, fontweight='bold')
    ax1.set_ylabel('Dorsoventral Position $Y$ (µm)\n(Ventral $\\leftarrow 0 \\rightarrow$ Dorsal)', fontsize=9.5, fontweight='bold')
    ax1.set_title('Virtual Silicon Probe Insertion (Laminae VII–IX)', fontsize=10.5, fontweight='bold', pad=8)
    ax1.grid(True, linestyle=':', alpha=0.4)
    ax1.legend(loc='upper right', fontsize=7.5, frameon=True)
    plt.colorbar(sc, ax=ax1, label='Channel Index (Tip $\\rightarrow$ Dorsal)')

    # 2. Histogram of Detected Units per Cell Type
    if probe.n_detected_units > 0:
        cell_types, counts = np.unique(probe.detected_cell_types, return_counts=True)
        bar_colors = [POP_COLORS.get(ct, '#888888') for ct in cell_types]
        bars = ax2.barh(cell_types, counts, color=bar_colors, edgecolor='black', lw=0.8)
        ax2.set_xlabel('Detected Unit Count', fontsize=9.5, fontweight='bold')
        ax2.set_title('Sampled Cell-Type Diversity', fontsize=10.5, fontweight='bold', pad=8)
        ax2.grid(True, linestyle=':', alpha=0.4, axis='x')
        for bar in bars:
            xval = bar.get_width()
            ax2.text(xval + 0.3, bar.get_y() + bar.get_height()/2.0, f"{int(xval)}", ha='left', va='center', fontsize=8.5, fontweight='bold')
    else:
        ax2.text(0.5, 0.5, 'No units in detection range', ha='center', va='center')

    plt.suptitle('Figure 6E: High-Density Silicon Probe Electrophysiological Sampling', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_6f_multichannel_spiking(
    probe: VirtualProbe,
    spikes: np.ndarray,
    estimated_rates: np.ndarray,
    time_ms: np.ndarray,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 6F: Multi-channel spike raster, smoothed rate heatmap, and polar phase progression along probe shank.
    """
    fig = plt.figure(figsize=(13, 7.5), dpi=dpi)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1])

    t_mask = (time_ms >= 4000) & (time_ms <= 6000)
    t_sec = (time_ms[t_mask] - 4000) / 1000.0

    # 1. Top Left: Channel-ordered Spike Raster Plot
    ax1 = fig.add_subplot(gs[0, 0])
    ch_spikes = spikes[t_mask, :]

    all_spk_t = []
    all_spk_ch = []
    for ch in range(probe.config.n_channels):
        units = probe.channel_neuron_map[ch]
        for u in units:
            spk_t = t_sec[ch_spikes[:, u]]
            if len(spk_t) > 0:
                all_spk_t.append(spk_t)
                all_spk_ch.append(np.full_like(spk_t, ch))
    if len(all_spk_t) > 0:
        ax1.scatter(np.concatenate(all_spk_t), np.concatenate(all_spk_ch), s=6, color='#2b5c8f', alpha=0.7)

    ax1.set_ylabel('Electrode Channel\n(0 = Ventral Tip $\\rightarrow$ 31 = Dorsal)', fontsize=9.5, fontweight='bold')
    ax1.set_title('Multi-Channel Spike Raster Along Probe Shank', fontsize=10.5, fontweight='bold', pad=6)
    ax1.set_ylim(-1, probe.config.n_channels)
    ax1.grid(True, linestyle=':', alpha=0.4)

    # 2. Bottom Left: Channel Multi-Unit Smoothed Rate Heatmap
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
    ch_mu_rates = np.zeros((np.sum(t_mask), probe.config.n_channels))
    for ch in range(probe.config.n_channels):
        units = probe.channel_neuron_map[ch]
        if len(units) > 0:
            ch_mu_rates[:, ch] = np.mean(estimated_rates[t_mask, :][:, units], axis=1)

    im2 = ax2.imshow(ch_mu_rates.T, aspect='auto', cmap='plasma', extent=[0, 2.0, 0, probe.config.n_channels], origin='lower')
    ax2.set_xlabel('Time (s)', fontsize=9.5, fontweight='bold')
    ax2.set_ylabel('Electrode Channel', fontsize=9.5, fontweight='bold')
    ax2.set_title('Instantaneous Multi-Unit Rate Heatmap', fontsize=10.5, fontweight='bold', pad=6)
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, label='Rate (Hz)')

    # 3. Right: Polar Phase Progression along Probe Depth
    ax3 = fig.add_subplot(gs[:, 1], projection='polar')
    phase_metrics = compute_channel_phase_lags(ch_mu_rates, dt_ms=1.0)
    phases_rad = phase_metrics['phase_lags_rad']
    active_chs = phase_metrics['active_channels']

    if len(active_chs) > 0:
        colors_ch = plt.cm.viridis(np.linspace(0, 1, len(active_chs)))
        for i, ch in enumerate(active_chs):
            phi = phases_rad[ch]
            radius = 0.3 + 0.65 * (ch / probe.config.n_channels)
            ax3.scatter([phi], [radius], color=colors_ch[i], s=50, edgecolor='black', lw=0.6, label=f"Ch {ch} ({int(np.degrees(phi))}°)" if i % 4 == 0 else None)
            ax3.annotate('', xy=(phi, radius), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=colors_ch[i], lw=1.2, alpha=0.7))

    ax3.set_title('Traveling Wave Phase Progression\nAcross Probe Recording Sites', fontsize=10.5, fontweight='bold', pad=12)
    ax3.set_ylim(0, 1.0)
    ax3.set_yticklabels([])
    ax3.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), fontsize=7.5, ncol=3, frameon=True)

    plt.suptitle('Figure 6F: High-Density Electrophysiological Validation of Traveling Wave Dynamics', fontsize=12.5, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def generate_figure6_complete(
    suite_data: Dict[str, Any],
    output_dir: str = "plots",
    dpi: int = 300
) -> Dict[str, str]:
    """
    Generates all 6 individual Figure 6 panels and the unified publication composite.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}

    ctrl_res = suite_data['control_res']
    les_res = suite_data['lesion_res']
    ctrl_net = suite_data['control_net']
    les_net = suite_data['lesion_net']
    reg_nets = suite_data['regrowth_nets']
    reg_results = suite_data['regrowth_results']
    probe = suite_data['probe']
    spikes = suite_data['spikes']
    est_rates = suite_data['estimated_rates']

    # 6A
    p6a = os.path.join(output_dir, "20_fig6a_lesion_projectome.png")
    fig6a = plot_panel_6a_lesion_projectome(ctrl_net, les_net, p6a, dpi=dpi)
    plt.close(fig6a)
    generated_files['panel_6a'] = p6a

    # 6B
    p6b = os.path.join(output_dir, "21_fig6b_post_lesion_dynamics.png")
    fig6b = plot_panel_6b_post_lesion_dynamics(ctrl_res, les_res, ctrl_net, les_net, p6b, dpi=dpi)
    plt.close(fig6b)
    generated_files['panel_6b'] = p6b

    # 6C
    p6c = os.path.join(output_dir, "22_fig6c_regrowth_comparison.png")
    fig6c = plot_panel_6c_regrowth_comparison(ctrl_net, les_net, reg_nets, p6c, dpi=dpi)
    plt.close(fig6c)
    generated_files['panel_6c'] = p6c

    # 6D
    p6d = os.path.join(output_dir, "23_fig6d_functional_recovery.png")
    fig6d = plot_panel_6d_functional_recovery(ctrl_res, les_res, reg_results, p6d, dpi=dpi)
    plt.close(fig6d)
    generated_files['panel_6d'] = p6d

    # 6E
    p6e = os.path.join(output_dir, "24_fig6e_probe_insertion.png")
    fig6e = plot_panel_6e_probe_insertion(ctrl_net, probe, p6e, dpi=dpi)
    plt.close(fig6e)
    generated_files['panel_6e'] = p6e

    # 6F
    p6f = os.path.join(output_dir, "25_fig6f_multichannel_spiking.png")
    fig6f = plot_panel_6f_multichannel_spiking(probe, spikes, est_rates, ctrl_res.time_ms, p6f, dpi=dpi)
    plt.close(fig6f)
    generated_files['panel_6f'] = p6f

    # Unified Composite Figure 6
    fig_comp = plt.figure(figsize=(18, 12), dpi=dpi)
    gs = fig_comp.add_gridspec(2, 3, height_ratios=[1, 1])

    # 6A (Top Left)
    ax_a = fig_comp.add_subplot(gs[0, 0])
    dz_ctrl, prof_ctrl = compute_projectome_1d_profile(ctrl_net, max_dist_um=4500.0)
    dz_les, prof_les = compute_projectome_1d_profile(les_net, max_dist_um=4500.0)
    ax_a.plot(dz_ctrl, prof_ctrl, color='#333333', lw=2.0, label='Intact Control')
    ax_a.plot(dz_les, prof_les, color='#e41a1c', lw=2.0, linestyle='--', label='Post-Lesion')
    ax_a.set_title('A: Transverse Lesion Projectome Disruption', fontweight='bold', fontsize=11)
    ax_a.set_xlabel('$\\Delta Z$ (µm)', fontsize=9)
    ax_a.set_ylabel('Net Synaptic Weight', fontsize=9)
    ax_a.legend(fontsize=8)
    ax_a.grid(True, linestyle=':', alpha=0.4)

    # 6B (Top Middle)
    ax_b = fig_comp.add_subplot(gs[0, 1])
    t_mask = (ctrl_res.time_ms >= 4000) & (ctrl_res.time_ms <= 6000)
    sort_idx = np.argsort(les_net.pos_z)
    r_les_s = les_res.rates[t_mask, :][:, sort_idx].T
    im_b = ax_b.imshow(r_les_s, aspect='auto', cmap='magma', extent=[0, 2.0, 0, les_net.n_neurons], origin='lower')
    ax_b.set_title('B: Post-Lesion Traveling Wave Arrest', fontweight='bold', fontsize=11)
    ax_b.set_xlabel('Time (s)', fontsize=9)
    ax_b.set_ylabel('Neuron ($T_{13} \\rightarrow S_4$)', fontsize=9)
    plt.colorbar(im_b, ax=ax_b, fraction=0.046, pad=0.04)

    # 6C (Top Right)
    ax_c = fig_comp.add_subplot(gs[0, 2])
    pop_names = [p.replace('regrowth_', '') for p in reg_nets.keys()]
    n_rest = [getattr(net, 'n_restored_synapses', 0) for net in reg_nets.values()]
    ax_c.bar(pop_names, n_rest, color=['#2ca02c', '#1f77b4', '#9467bd', '#ff7f0e'][:len(pop_names)], edgecolor='black', width=0.55)
    ax_c.set_title('C: Targeted Axonal Regrowth Capacity', fontweight='bold', fontsize=11)
    ax_c.set_ylabel('Restored Synapses', fontsize=9)
    ax_c.grid(True, linestyle=':', alpha=0.4, axis='y')

    # 6D (Bottom Left)
    ax_d = fig_comp.add_subplot(gs[1, 0])
    v2a_res, _, v2a_net = reg_results.get('regrowth_V2a-2', (ctrl_res, {}, ctrl_net))
    r_v2a_s = v2a_res.rates[t_mask, :][:, sort_idx].T
    im_d = ax_d.imshow(r_v2a_s, aspect='auto', cmap='magma', extent=[0, 2.0, 0, v2a_net.n_neurons], origin='lower')
    ax_d.set_title('D: Rescued Locomotion (V2a-2 Regrowth)', fontweight='bold', fontsize=11)
    ax_d.set_xlabel('Time (s)', fontsize=9)
    ax_d.set_ylabel('Neuron ($T_{13} \\rightarrow S_4$)', fontsize=9)
    plt.colorbar(im_d, ax=ax_d, fraction=0.046, pad=0.04)

    # 6E (Bottom Middle)
    ax_e = fig_comp.add_subplot(gs[1, 1])
    ax_e.scatter(ctrl_net.pos_x, ctrl_net.pos_y, s=4, color='#bbbbbb', alpha=0.3)
    ax_e.plot(probe.channel_positions_um[:, 0], probe.channel_positions_um[:, 1], color='#333333', lw=2.5)
    sc_e = ax_e.scatter(probe.channel_positions_um[:, 0], probe.channel_positions_um[:, 1], c=np.arange(probe.config.n_channels), cmap='viridis', s=35, edgecolor='black', zorder=4)
    if probe.n_detected_units > 0:
        ax_e.scatter(ctrl_net.pos_x[probe.detected_neuron_indices], ctrl_net.pos_y[probe.detected_neuron_indices], c=probe.channel_assignments, cmap='viridis', s=25, edgecolor='red', lw=0.6)
    ax_e.set_title('E: Virtual 32-ch Probe Sampling', fontweight='bold', fontsize=11)
    ax_e.set_xlabel('Mediolateral $X$ (µm)', fontsize=9)
    ax_e.set_ylabel('Dorsoventral $Y$ (µm)', fontsize=9)
    plt.colorbar(sc_e, ax=ax_e, label='Channel')

    # 6F (Bottom Right)
    ax_f = fig_comp.add_subplot(gs[1, 2], projection='polar')
    ch_mu = np.zeros((np.sum(t_mask), probe.config.n_channels))
    for ch in range(probe.config.n_channels):
        units = probe.channel_neuron_map[ch]
        if len(units) > 0:
            ch_mu[:, ch] = np.mean(est_rates[t_mask, :][:, units], axis=1)
    ph_m = compute_channel_phase_lags(ch_mu, dt_ms=1.0)
    for ch in ph_m['active_channels']:
        phi = ph_m['phase_lags_rad'][ch]
        rad = 0.3 + 0.65 * (ch / probe.config.n_channels)
        ax_f.scatter([phi], [rad], c=[plt.cm.viridis(ch / probe.config.n_channels)], s=45, edgecolor='black', lw=0.5)
    ax_f.set_title('F: Traveling Wave Phase Lags on Probe', fontweight='bold', fontsize=11, pad=10)
    ax_f.set_ylim(0, 1.0)
    ax_f.set_yticklabels([])

    fig_comp.suptitle('Figure 6: Spinal Cord Lesion, Targeted Axonal Regrowth, and High-Density Electrophysiology (Komi et al. 2026)', fontsize=14, fontweight='bold', y=0.99)
    plt.tight_layout()

    p_comp = os.path.join(output_dir, "26_figure6_complete.png")
    fig_comp.savefig(p_comp, bbox_inches='tight', dpi=dpi)
    plt.close(fig_comp)
    generated_files['figure6_complete'] = p_comp

    return generated_files
