"""
Figure 4 Publication-Quality Multi-Panel Generator: Speed and Gait Control.
Faithfully reproduces Figure 4 of Komi et al., Nature Communications, 2026:
- 4A: Compound tanh gain modulation curves
- 4B: Descending brainstem terminal maps (LPGi & Raphe 5-HT)
- 4C: Speed acceleration under descending drive ramp
- 4D: Multi-gait locomotor EMG patterns (Walk, Trot, Bound)
- 4E: Polar phase transitions (Left-Right and Flexor-Extensor)
- 4F/G: Locomotor frequency and amplitude quantification across gaits
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List

from dynamics import tanh_activation
from locomotion import generate_synthetic_emg, MUSCLE_FLEX_EXT
from figure3_analysis import POP_COLORS, MUSCLE_COLORS


def plot_panel_4a_tanh_gain_curves(
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 4A: Input-output compound hyperbolic tangent activation curves
    across different neuromodulatory gain factors g in [0.5, 0.7, 1.0, 1.5, 2.0, 3.0].
    """
    fig, ax = plt.subplots(figsize=(6, 5), dpi=dpi)
    
    v_vec = np.linspace(-30.0, 120.0, 500)
    gains = [0.5, 0.7, 1.0, 1.5, 2.0, 3.0]
    gain_colors = plt.cm.viridis(np.linspace(0.1, 0.95, len(gains)))
    
    threshold = 20.0
    f_max = 50.0

    for g_val, col in zip(gains, gain_colors):
        rates = tanh_activation(v_vec, threshold, g_val, f_max)
        ax.plot(v_vec, rates, label=f'Gain $g = {g_val}$', color=col, linewidth=2.2)

    ax.axvline(threshold, color='#666666', linestyle='--', alpha=0.7, label=f'Threshold $T = {int(threshold)}$ mV')
    ax.axhline(f_max, color='#999999', linestyle=':', alpha=0.7, label=f'$f_{{max}} = {int(f_max)}$ Hz')

    ax.set_xlabel('Effective Membrane Potential $(V - a)$ (mV)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Firing Rate $R$ (Hz)', fontsize=11, fontweight='bold')
    ax.set_title('Figure 4A: Compound $\\tanh$ Gain Modulation', fontsize=12, fontweight='bold', pad=10)
    ax.set_xlim(-30.0, 120.0)
    ax.set_ylim(-2.0, 65.0)
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend(loc='upper left', fontsize=9, frameon=True)

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_4b_descending_tract_maps(
    network: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 4B: Transverse spatial cross-section illustrating descending tract
    termination territories (LPGi glutamatergic & glycinergic, Raphe 5-HT).
    """
    fig, ax = plt.subplots(figsize=(7, 6), dpi=dpi)

    # Plot background spinal cord neurons
    ax.scatter(network.pos_x, network.pos_y, c='#e0e0e0', s=4, alpha=0.4, label='Spinal Neurons')

    # Highlight specific cell populations targeted by descending pathways
    v2a_mask = np.isin(network.types, ['V2a-1', 'V2a-2'])
    v0v_mask = (network.types == 'V0v')
    mn_mask = (network.types == 'MN')

    ax.scatter(network.pos_x[v2a_mask], network.pos_y[v2a_mask], c=POP_COLORS['V2a-1'], s=8, alpha=0.7, label='V2a (LPGi/5-HT target)')
    ax.scatter(network.pos_x[v0v_mask], network.pos_y[v0v_mask], c=POP_COLORS['V0v'], s=8, alpha=0.7, label='V0v (LPGi target)')
    ax.scatter(network.pos_x[mn_mask], network.pos_y[mn_mask], c=POP_COLORS['MN'], s=12, alpha=0.8, label='MN (Motor Output)')

    # Load descending tract polygons if available
    try:
        tracts = network.data_loader.load_descending_tracts()
        if 'LPGIVglutL' in tracts and isinstance(tracts['LPGIVglutL'], np.ndarray):
            poly_l = tracts['LPGIVglutL']
            poly_r = tracts.get('LPGIVglutR', tracts['LPGIVglutL'])
            if poly_l.shape[1] == 2:
                p1 = Polygon(poly_l, closed=True, fill=False, edgecolor='#d95f02', linewidth=2.0, linestyle='--', label='LPGi Glutamatergic ROI')
                ax.add_patch(p1)
            if poly_r.shape[1] == 2:
                p2 = Polygon(poly_r, closed=True, fill=False, edgecolor='#d95f02', linewidth=2.0, linestyle='--')
                ax.add_patch(p2)
    except Exception:
        pass

    ax.set_xlabel('Mediolateral Axis (µm)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Dorsoventral Axis (µm)', fontsize=11, fontweight='bold')
    ax.set_title('Figure 4B: Descending Brainstem Terminal Zones', fontsize=12, fontweight='bold', pad=10)
    ax.legend(loc='upper right', fontsize=8.5, frameon=True)
    ax.set_aspect('equal', 'box')
    ax.grid(True, linestyle=':', alpha=0.4)

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_4c_descending_ramp(
    sim_result: Any,
    I_ramp: np.ndarray,
    network: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 4C: Acceleration of locomotor rhythm under a linearly ramped descending drive current.
    """
    fig, (ax_top, ax_mid, ax_bot) = plt.subplots(3, 1, figsize=(10, 8), dpi=dpi, sharex=True, gridspec_kw={'height_ratios': [1, 2.5, 1.5]})

    time_sec = sim_result.time_ms / 1000.0

    # Top: Descending Drive Current
    ax_top.plot(time_sec, I_ramp, color='#d95f02', linewidth=2.5)
    ax_top.set_ylabel('$I_{\\text{desc}}$ (pA)', fontsize=10, fontweight='bold')
    ax_top.set_title('Figure 4C: Locomotor Acceleration Under Descending Drive Ramp', fontsize=12, fontweight='bold', pad=10)
    ax_top.grid(True, linestyle=':', alpha=0.5)

    # Mid: Space-Time Activity Wave Raster (sorted by Z rostrocaudal position)
    rates = sim_result.rates
    sort_z_idx = np.argsort(network.pos_z)
    sub_idx = sort_z_idx[::10]  # Subsample for rendering speed
    im = ax_mid.imshow(
        rates[:, sub_idx].T,
        aspect='auto',
        origin='lower',
        cmap='magma',
        extent=(float(time_sec[0]), float(time_sec[-1]), 0.0, float(len(sub_idx))),
        vmin=0.0,
        vmax=float(np.percentile(rates, 99))
    )
    ax_mid.set_ylabel('Neuron (Rostral $\\to$ Caudal)', fontsize=10, fontweight='bold')
    cbar = fig.colorbar(im, ax=ax_mid, orientation='vertical', pad=0.01)
    cbar.set_label('Rate (Hz)', fontsize=9)

    # Bot: Mean Population Firing Rate Trajectories
    for pop in ['V2a-1', 'V1', 'MN']:
        if pop in sim_result.population_rates:
            ax_bot.plot(time_sec, sim_result.population_rates[pop], color=POP_COLORS.get(pop, '#333333'), label=pop, linewidth=1.5)
    ax_bot.set_xlabel('Time (s)', fontsize=11, fontweight='bold')
    ax_bot.set_ylabel('Mean Rate (Hz)', fontsize=10, fontweight='bold')
    ax_bot.legend(loc='upper left', fontsize=9, ncol=3, frameon=True)
    ax_bot.grid(True, linestyle=':', alpha=0.5)

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_4d_gait_emg_patterns(
    gait_results: Dict[str, Tuple[Any, Dict[str, Any]]],
    network: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 4D: Multi-muscle synthetic EMG signals across distinct gaits (Walk, Trot, Bound).
    """
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), dpi=dpi, sharex=False)

    gait_names = ['walk', 'trot', 'bound']
    titles = ['Slow Walk ($I_e = 20$ pA, $f \\approx 2$ Hz)', 'Moderate Trot ($I_e = 30$ pA, $f \\approx 4$ Hz)', 'High-Speed Bound ($I_e = 45$ pA, $g_{\\text{5HT}} = 1.75\\times$, $f \\approx 7$ Hz)']

    target_muscles = ['Tibialis Anterior', 'Gastrocnemius']

    for ax, g_name, title in zip(axes, gait_names, titles):
        if g_name not in gait_results:
            continue
        sim_res, metrics = gait_results[g_name]
        emg_data = generate_synthetic_emg(
            rates=sim_res.rates,
            neuron_types=network.types,
            neuron_lat=network.latera,
            neuron_z=network.pos_z,
            time_ms=sim_res.time_ms,
            noise_level=0.15,
            window_ms=20,
            rng_seed=42
        )
        
        # Display 1.5 seconds of steady-state locomotion
        t_mask = (sim_res.time_ms >= 4000) & (sim_res.time_ms <= 5500)
        t_sub = (sim_res.time_ms[t_mask] - 4000) / 1000.0

        offset = 0.0
        for m_name in target_muscles:
            for side in ['Left', 'Right']:
                if side in emg_data and m_name in emg_data[side]['muscles']:
                    m_idx = list(emg_data[side]['muscles']).index(m_name)
                    env = emg_data[side]['envelope'][t_mask, m_idx]
                    raw = emg_data[side]['raw_emg'][t_mask, m_idx]
                    col = MUSCLE_COLORS['Flex'] if 'Tibialis' in m_name else MUSCLE_COLORS['Ext']
                    line_style = '-' if side == 'Left' else '--'
                    
                    # Plot raw signal faded, envelope bold
                    ax.plot(t_sub, raw + offset, color='#cccccc', linewidth=0.5, alpha=0.6)
                    ax.plot(t_sub, env + offset, color=col, linestyle=line_style, linewidth=2.0, label=f"{side[0]} {m_name}")
                    offset += 1.2 * max(float(np.max(env)), 0.5)

        ax.set_title(f"Figure 4D: {title} — Detected: {metrics['gait_detected']}", fontsize=11, fontweight='bold', pad=8)
        ax.set_ylabel('Synthetic EMG (a.u.)', fontsize=9.5, fontweight='bold')
        ax.set_yticks([])
        ax.grid(True, linestyle=':', alpha=0.4)
        if ax == axes[0]:
            ax.legend(loc='upper right', bbox_to_anchor=(1.22, 1.0), fontsize=8.5, frameon=True)

    axes[-1].set_xlabel('Time (s)', fontsize=11, fontweight='bold')

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_4e_polar_phase_transitions(
    gait_results: Dict[str, Tuple[Any, Dict[str, Any]]],
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 4E: Polar circular plots demonstrating the Left-Right phase transition
    (alternation ~pi -> synchrony ~0) while maintaining intralimb flexor-extensor alternation.
    """
    fig, (ax_lr, ax_fe) = plt.subplots(1, 2, figsize=(10, 5), dpi=dpi, subplot_kw={'projection': 'polar'})

    gait_colors = {'walk': '#2ca02c', 'trot': '#1f77b4', 'bound': '#d62728'}
    gait_labels = {'walk': 'Walk (Slow)', 'trot': 'Trot (Medium)', 'bound': 'Bound (Fast)'}

    for g_name in ['walk', 'trot', 'bound']:
        if g_name not in gait_results:
            continue
        _, metrics = gait_results[g_name]
        col = gait_colors.get(g_name, '#333333')
        lbl = gait_labels.get(g_name, g_name.capitalize())

        lr_phi = metrics['lr_phase_rad']
        fe_phi = metrics['fe_phase_rad']

        # Plot vector arrow on polar axes
        ax_lr.annotate('', xy=(lr_phi, 0.9), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color=col, lw=2.5, mutation_scale=15))
        ax_lr.scatter([lr_phi], [0.9], color=col, s=80, label=f"{lbl}: {metrics['lr_phase_deg']:.1f}°")

        ax_fe.annotate('', xy=(fe_phi, 0.9), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color=col, lw=2.5, mutation_scale=15))
        ax_fe.scatter([fe_phi], [0.9], color=col, s=80, label=f"{lbl}: {metrics['fe_phase_deg']:.1f}°")

    ax_lr.set_title('Left–Right L2 Phase ($\\Delta \\phi_{\\text{L-R}}$)\nAlternation $\\to$ Synchrony', fontsize=11, fontweight='bold', pad=15)
    ax_lr.set_ylim(0.0, 1.1)
    ax_lr.set_yticklabels([])
    ax_lr.legend(loc='lower left', bbox_to_anchor=(-0.25, -0.2), fontsize=8.5, frameon=True)

    ax_fe.set_title('Ipsilateral L2–L5 Phase ($\\Delta \\phi_{\\text{F-E}}$)\nFlexor–Extensor Coordination', fontsize=11, fontweight='bold', pad=15)
    ax_fe.set_ylim(0.0, 1.1)
    ax_fe.set_yticklabels([])
    ax_fe.legend(loc='lower right', bbox_to_anchor=(1.25, -0.2), fontsize=8.5, frameon=True)

    plt.suptitle('Figure 4E: Polar Gait Phase Transitions', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_4fg_frequency_amplitude(
    sweep_df: pd.DataFrame,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panels 4F and 4G: Monotonic frequency-current and amplitude-current curves across descending drive sweep.
    """
    fig, (ax_f, ax_a) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=dpi)

    I_e = np.asarray(sweep_df['I_e'].to_numpy(), dtype=np.float64)
    freq = np.asarray(sweep_df['frequency_hz'].to_numpy(), dtype=np.float64)
    amp = np.asarray(sweep_df['rms_amplitude_hz'].to_numpy(), dtype=np.float64)
    gait_states = sweep_df['gait_state'].to_numpy()

    # Color code markers by classified gait state
    state_colors = {'Walk': '#2ca02c', 'Trot': '#1f77b4', 'Bound': '#d62728', 'Transition': '#ff7f0e'}

    # 4F: Frequency vs Descending Drive
    ax_f.plot(I_e, freq, color='#333333', linestyle='-', linewidth=2.0, zorder=1)
    for state in ['Walk', 'Trot', 'Bound', 'Transition']:
        mask = (gait_states == state)
        if np.any(mask):
            ax_f.scatter(I_e[mask], freq[mask], color=state_colors.get(state, '#333333'), s=70, label=state, zorder=2)

    ax_f.set_xlabel('Descending Drive Current $I_e$ (pA)', fontsize=11, fontweight='bold')
    ax_f.set_ylabel('Locomotor Frequency (Hz)', fontsize=11, fontweight='bold')
    ax_f.set_title('Figure 4F: Locomotor Frequency vs Drive', fontsize=12, fontweight='bold', pad=10)
    ax_f.grid(True, linestyle=':', alpha=0.5)
    if ax_f.get_legend_handles_labels()[1]:
        ax_f.legend(loc='upper left', fontsize=9, frameon=True)

    # 4G: Burst Amplitude vs Descending Drive
    ax_a.plot(I_e, amp, color='#333333', linestyle='-', linewidth=2.0, zorder=1)
    for state in ['Walk', 'Trot', 'Bound', 'Transition']:
        mask = (gait_states == state)
        if np.any(mask):
            ax_a.scatter(I_e[mask], amp[mask], color=state_colors.get(state, '#333333'), s=70, label=state, zorder=2)

    ax_a.set_xlabel('Descending Drive Current $I_e$ (pA)', fontsize=11, fontweight='bold')
    ax_a.set_ylabel('RMS Firing Rate Amplitude (Hz)', fontsize=11, fontweight='bold')
    ax_a.set_title('Figure 4G: Motor Output Amplitude vs Drive', fontsize=12, fontweight='bold', pad=10)
    ax_a.grid(True, linestyle=':', alpha=0.5)
    if ax_a.get_legend_handles_labels()[1]:
        ax_a.legend(loc='lower right', fontsize=9, frameon=True)

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def generate_figure4_complete(
    network: Any,
    gait_results: Dict[str, Tuple[Any, Dict[str, Any]]],
    ramp_res: Tuple[Any, np.ndarray],
    sweep_df: pd.DataFrame,
    output_dir: str = "plots",
    dpi: int = 300
) -> Dict[str, str]:
    """
    Generates all individual Figure 4 panels as well as the composite multi-panel summary figure.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}

    p4a = os.path.join(output_dir, "06_fig4a_tanh_gain_curves.png")
    fig4a = plot_panel_4a_tanh_gain_curves(p4a, dpi=dpi)
    plt.close(fig4a)
    generated_files['panel_4a'] = p4a

    p4b = os.path.join(output_dir, "07_fig4b_descending_tract_maps.png")
    fig4b = plot_panel_4b_descending_tract_maps(network, p4b, dpi=dpi)
    plt.close(fig4b)
    generated_files['panel_4b'] = p4b

    p4c = os.path.join(output_dir, "08_fig4c_descending_drive_ramp.png")
    fig4c = plot_panel_4c_descending_ramp(ramp_res[0], ramp_res[1], network, p4c, dpi=dpi)
    plt.close(fig4c)
    generated_files['panel_4c'] = p4c

    p4d = os.path.join(output_dir, "09_fig4d_gait_patterns_emg.png")
    fig4d = plot_panel_4d_gait_emg_patterns(gait_results, network, p4d, dpi=dpi)
    plt.close(fig4d)
    generated_files['panel_4d'] = p4d

    p4e = os.path.join(output_dir, "10_fig4e_polar_phase_transitions.png")
    fig4e = plot_panel_4e_polar_phase_transitions(gait_results, p4e, dpi=dpi)
    plt.close(fig4e)
    generated_files['panel_4e'] = p4e

    p4fg = os.path.join(output_dir, "11_fig4fg_frequency_amplitude_quantification.png")
    fig4fg = plot_panel_4fg_frequency_amplitude(sweep_df, p4fg, dpi=dpi)
    plt.close(fig4fg)
    generated_files['panel_4fg'] = p4fg

    # Generate Composite Summary Figure 4
    fig_comp = plt.figure(figsize=(16, 12), dpi=dpi)
    gs = fig_comp.add_gridspec(3, 3, height_ratios=[1, 1.2, 1])

    # Subplot 1: Gain curves (Row 0, Col 0)
    ax1 = fig_comp.add_subplot(gs[0, 0])
    v_vec = np.linspace(-20, 100, 300)
    for g_val, col in zip([0.7, 1.0, 2.0], ['#1f77b4', '#2ca02c', '#d62728']):
        ax1.plot(v_vec, tanh_activation(v_vec, 20.0, g_val, 50.0), label=f'$g={g_val}$', color=col, lw=2)
    ax1.set_title('A: $\\tanh$ Gain Modulation', fontweight='bold', fontsize=11)
    ax1.set_xlabel('Potential (mV)', fontsize=9)
    ax1.set_ylabel('Rate (Hz)', fontsize=9)
    ax1.legend(fontsize=8)
    ax1.grid(True, linestyle=':', alpha=0.5)

    # Subplot 2: Descending target tracts (Row 0, Col 1)
    ax2 = fig_comp.add_subplot(gs[0, 1])
    ax2.scatter(network.pos_x, network.pos_y, c='#e0e0e0', s=2, alpha=0.3)
    v2a_m = np.isin(network.types, ['V2a-1', 'V2a-2'])
    ax2.scatter(network.pos_x[v2a_m], network.pos_y[v2a_m], c=POP_COLORS['V2a-1'], s=5, label='V2a (LPGi/5-HT)')
    ax2.scatter(network.pos_x[network.types == 'MN'], network.pos_y[network.types == 'MN'], c=POP_COLORS['MN'], s=8, label='MN')
    ax2.set_title('B: Descending Target Zones', fontweight='bold', fontsize=11)
    ax2.set_xlabel('ML (µm)', fontsize=9)
    ax2.set_ylabel('DV (µm)', fontsize=9)
    ax2.legend(fontsize=8)

    # Subplot 3: Polar phase transitions (Row 0, Col 2, projection='polar')
    ax3 = fig_comp.add_subplot(gs[0, 2], projection='polar')
    for g_name, col in zip(['walk', 'trot', 'bound'], ['#2ca02c', '#1f77b4', '#d62728']):
        if g_name in gait_results:
            phi = gait_results[g_name][1]['lr_phase_rad']
            ax3.annotate('', xy=(phi, 0.9), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=2))
            ax3.scatter([phi], [0.9], color=col, s=50, label=g_name.capitalize())
    ax3.set_title('E: Left–Right Phase Transitions', fontweight='bold', fontsize=11, pad=10)
    ax3.set_ylim(0.0, 1.1)
    ax3.set_yticklabels([])
    ax3.legend(fontsize=8, loc='lower left')

    # Subplot 4: Descending drive acceleration ramp (Row 1, Col 0:2)
    ax4 = fig_comp.add_subplot(gs[1, :2])
    rates = ramp_res[0].rates
    t_sec = ramp_res[0].time_ms / 1000.0
    im4 = ax4.imshow(
        rates[:, ::15].T,
        aspect='auto',
        origin='lower',
        cmap='magma',
        extent=(float(t_sec[0]), float(t_sec[-1]), 0.0, float(rates.shape[1] // 15))
    )
    ax4.set_title('C: Rhythm Acceleration Under Descending Drive Ramp ($I_e: 15 \\to 50$ pA)', fontweight='bold', fontsize=11)
    ax4.set_xlabel('Time (s)', fontsize=9)
    ax4.set_ylabel('Neuron (RC sorted)', fontsize=9)

    # Subplot 5: Synthetic EMG gaits (Row 1, Col 2)
    ax5 = fig_comp.add_subplot(gs[1, 2])
    if 'trot' in gait_results:
        sim_trot = gait_results['trot'][0]
        emg_trot = generate_synthetic_emg(
            rates=sim_trot.rates,
            neuron_types=network.types,
            neuron_lat=network.latera,
            neuron_z=network.pos_z,
            time_ms=sim_trot.time_ms,
            noise_level=0.15,
            window_ms=20,
            rng_seed=42
        )
        t_mask = (sim_trot.time_ms >= 4000) & (sim_trot.time_ms <= 5000)
        t_s = (sim_trot.time_ms[t_mask] - 4000) / 1000.0
        if 'Left' in emg_trot and 'Tibialis Anterior' in emg_trot['Left']['muscles']:
            ta_idx = list(emg_trot['Left']['muscles']).index('Tibialis Anterior')
            ax5.plot(t_s, emg_trot['Left']['envelope'][t_mask, ta_idx], color='#377eb8', label='L-TA (Flex)', lw=1.8)
        if 'Left' in emg_trot and 'Gastrocnemius' in emg_trot['Left']['muscles']:
            gm_idx = list(emg_trot['Left']['muscles']).index('Gastrocnemius')
            ax5.plot(t_s, emg_trot['Left']['envelope'][t_mask, gm_idx], color='#ff7f00', label='L-GM (Ext)', lw=1.8)
    ax5.set_title('D: Trotting Reciprocal EMG', fontweight='bold', fontsize=11)
    ax5.set_xlabel('Time (s)', fontsize=9)
    ax5.set_ylabel('Envelope (a.u.)', fontsize=9)
    ax5.legend(fontsize=8)

    # Subplot 6: Frequency vs Drive (Row 2, Col 0:2)
    ax6 = fig_comp.add_subplot(gs[2, :2])
    ax6.plot(sweep_df['I_e'], sweep_df['frequency_hz'], color='#333333', lw=2)
    ax6.scatter(sweep_df['I_e'], sweep_df['frequency_hz'], c='#d95f02', s=50)
    ax6.set_title('F: Locomotor Frequency vs Descending Drive Current', fontweight='bold', fontsize=11)
    ax6.set_xlabel('Descending Current $I_e$ (pA)', fontsize=9)
    ax6.set_ylabel('Frequency (Hz)', fontsize=9)
    ax6.grid(True, linestyle=':', alpha=0.5)

    # Subplot 7: Amplitude vs Drive (Row 2, Col 2)
    ax7 = fig_comp.add_subplot(gs[2, 2])
    ax7.plot(sweep_df['I_e'], sweep_df['rms_amplitude_hz'], color='#333333', lw=2)
    ax7.scatter(sweep_df['I_e'], sweep_df['rms_amplitude_hz'], c='#7570b3', s=50)
    ax7.set_title('G: Output Amplitude vs Drive', fontweight='bold', fontsize=11)
    ax7.set_xlabel('$I_e$ (pA)', fontsize=9)
    ax7.set_ylabel('RMS Amplitude (Hz)', fontsize=9)
    ax7.grid(True, linestyle=':', alpha=0.5)

    fig_comp.suptitle('Figure 4: Speed and Gait Control in the Mouse Spinal Projectome Model (Komi et al. 2026)', fontsize=14, fontweight='bold', y=0.99)
    plt.tight_layout()

    p_comp = os.path.join(output_dir, "12_figure4_complete.png")
    fig_comp.savefig(p_comp, bbox_inches='tight', dpi=dpi)
    plt.close(fig_comp)
    generated_files['figure4_complete'] = p_comp

    return generated_files
