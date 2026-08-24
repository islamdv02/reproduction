"""
Figure 3 Publication-Quality Visualization and Multi-Panel Generator.
Reproduces Figure 3 of Komi et al., Nature Communications, 2026:
- 3a: 3D Spinal cord projectome layout
- 3b/c: Population firing rates over time
- 3d: Hindlimb muscle EMG signals with flexor/extensor alternating phase
- 3e: Rostrocaudal spatiotemporal traveling wave propagation
- 3f/g: Low-dimensional neural manifold / PCA rotational dynamics
- 3h: Polar inter-population phase relationships
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import Dict, Any, Optional

from locomotion import (
    generate_synthetic_emg,
    compute_traveling_wave,
    compute_pca_dynamics,
    compute_population_phases
)

# Canonical BergLab color palette
POP_COLORS = {
    'V1': '#377eb8',     # Blue
    'V2a-1': '#e41a1c',  # Red
    'V2a-2': '#ff7f00',  # Orange
    'V2b': '#984ea3',    # Purple
    'V0d': '#4daf4a',    # Green
    'V0v': '#a65628',    # Brown
    'dI6': '#f781bf',    # Pink
    'V3': '#666666',     # Grey
    'MN': '#1b9e77'      # Teal
}

MUSCLE_COLORS = {
    'Flex': '#377eb8',  # Berg Blue (Flexor)
    'Ext': '#ff7f00'    # Berg Orange (Extensor)
}


def generate_figure3_complete(
    network: Any,
    sim_result: Any,
    output_dir: str = "plots",
    dpi: int = 300
) -> Dict[str, str]:
    """
    Generates all panels of Figure 3 as well as the unified multi-panel figure.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}

    time_ms = sim_result.time_ms
    rates = sim_result.rates
    pop_rates = sim_result.population_rates

    # Steady-state time window (1000 - 3000 ms for detailed views)
    t_zoom_mask = (time_ms >= 1000) & (time_ms <= 3000)
    t_zoom = time_ms[t_zoom_mask]

    # Compute locomotion metrics
    emg_data = generate_synthetic_emg(
        rates=rates,
        neuron_types=network.types,
        neuron_lat=network.pos_x,
        neuron_z=network.pos_z,
        time_ms=time_ms,
        noise_level=0.15,
        window_ms=20,
        rng_seed=42
    )

    wave_data = compute_traveling_wave(
        rates=rates,
        neuron_z=network.pos_z,
        dt_ms=1.0,
        t_start_ms=1000,
        n_spatial_bins=20
    )

    pca_data = compute_pca_dynamics(
        rates=rates,
        n_components=3,
        t_start_ms=1000
    )

    phase_data = compute_population_phases(
        population_rates=pop_rates,
        dt_ms=1.0,
        t_start_ms=1000,
        reference_pop='V2a-1'
    )

    # -------------------------------------------------------------
    # 1. Unified Multi-Panel Figure 3
    # -------------------------------------------------------------
    fig = plt.figure(figsize=(16, 12), dpi=dpi)
    
    # Panel 3a: 3D Network Anatomy
    ax_3a = fig.add_subplot(2, 3, 1, projection='3d')
    for pop_name, color in POP_COLORS.items():
        mask = (network.types == pop_name)
        if np.any(mask):
            ax_3a.scatter(
                network.pos_x[mask],
                network.pos_y[mask],
                network.pos_z[mask],
                c=color,
                s=4,
                alpha=0.6,
                label=pop_name,
                edgecolors='none'
            )
    ax_3a.set_title('a  Spinal Projectome Layout', fontsize=11, fontweight='bold', loc='left')
    ax_3a.set_xlabel('ML (µm)', fontsize=8)
    ax_3a.set_ylabel('DV (µm)', fontsize=8)
    ax_3a.set_zlabel('RC (µm)', fontsize=8)
    ax_3a.view_init(elev=20, azim=-55)
    ax_3a.tick_params(labelsize=7)

    # Panel 3b/c: Population Firing Rates
    ax_3bc = fig.add_subplot(2, 3, 2)
    for pop_name, p_rate in pop_rates.items():
        color = POP_COLORS.get(pop_name, '#333333')
        ax_3bc.plot(t_zoom, p_rate[t_zoom_mask], color=color, linewidth=1.4, label=pop_name)
    ax_3bc.set_title('b,c  Population Firing Rates', fontsize=11, fontweight='bold', loc='left')
    ax_3bc.set_xlabel('Time (ms)', fontsize=9)
    ax_3bc.set_ylabel('Firing Rate (Hz)', fontsize=9)
    ax_3bc.grid(True, linestyle=':', alpha=0.5)
    ax_3bc.legend(loc='upper right', ncol=3, fontsize=7, frameon=True)
    ax_3bc.tick_params(labelsize=8)

    # Panel 3d: Hindlimb Muscle EMG with Stance/Swing Shading
    ax_3d = fig.add_subplot(2, 3, 3)
    r_emg = emg_data['Right']
    muscles = r_emg['muscles']
    envelopes = r_emg['envelope'][t_zoom_mask, :]
    flex_ext = r_emg['flex_ext']
    
    # Stance shading
    for (t_start, t_end) in r_emg['stance_swing_bounds']:
        if t_end >= t_zoom[0] and t_start <= t_zoom[-1]:
            ax_3d.axvspan(max(t_start, t_zoom[0]), min(t_end, t_zoom[-1]), color='#e0e0e0', alpha=0.5, lw=0)

    for m_i, m_name in enumerate(muscles):
        c = MUSCLE_COLORS[flex_ext[m_i]]
        offset = (len(muscles) - 1 - m_i) * 35.0
        env_scaled = envelopes[:, m_i]
        ax_3d.plot(t_zoom, env_scaled + offset, color=c, linewidth=1.5)
        ax_3d.text(t_zoom[0] - 20, offset + 10, f"{m_name} ({flex_ext[m_i]})", ha='right', va='center', fontsize=7, fontweight='bold', color=c)
    
    ax_3d.set_title('d  Hindlimb Muscle EMG (Right)', fontsize=11, fontweight='bold', loc='left')
    ax_3d.set_xlabel('Time (ms)', fontsize=9)
    ax_3d.set_yticks([])
    ax_3d.set_xlim(t_zoom[0] - 150, t_zoom[-1] + 20)
    ax_3d.grid(True, linestyle=':', alpha=0.3, axis='x')
    ax_3d.tick_params(labelsize=8)

    # Panel 3e: Rostrocaudal Traveling Wave
    ax_3e = fig.add_subplot(2, 3, 4)
    z_sort = np.argsort(network.pos_z)
    rates_sorted = rates[t_zoom_mask, :][:, z_sort].T
    im_3e = ax_3e.imshow(
        rates_sorted,
        aspect='auto',
        cmap='viridis',
        origin='lower',
        extent=[t_zoom[0], t_zoom[-1], network.pos_z[z_sort][0], network.pos_z[z_sort][-1]]
    )
    plt.colorbar(im_3e, ax=ax_3e, label='Rate (Hz)', fraction=0.046, pad=0.04)
    ax_3e.set_title(f"e  Traveling Wave (v = {wave_data['wave_velocity_mm_s']:.2f} mm/s)", fontsize=11, fontweight='bold', loc='left')
    ax_3e.set_xlabel('Time (ms)', fontsize=9)
    ax_3e.set_ylabel('RC Position Z (µm)', fontsize=9)
    ax_3e.tick_params(labelsize=8)

    # Panel 3f/g: PCA Dynamics & Neural Manifold Limit Cycle
    ax_3fg = fig.add_subplot(2, 3, 5, projection='3d')
    pcs_zoom = pca_data['pcs'][:len(t_zoom), :]
    
    # 3D trajectory
    ax_3fg.plot(pcs_zoom[:, 0], pcs_zoom[:, 1], pcs_zoom[:, 2], color='#2b5c8f', linewidth=1.5, alpha=0.9)
    ax_3fg.scatter(pcs_zoom[0, 0], pcs_zoom[0, 1], pcs_zoom[0, 2], color='red', s=30, label='Start')
    
    # Projections on planes
    z_min_pc = np.min(pcs_zoom[:, 2]) - 5
    ax_3fg.plot(pcs_zoom[:, 0], pcs_zoom[:, 1], np.full_like(pcs_zoom[:, 2], z_min_pc), color='gray', alpha=0.3, lw=1)
    
    var_exp = pca_data['explained_variance_ratio'] * 100.0
    ax_3fg.set_title(f'f,g  PCA Manifold (Top 3: {pca_data["cumulative_variance"][2]*100:.1f}%)', fontsize=11, fontweight='bold', loc='left')
    ax_3fg.set_xlabel(f'PC1 ({var_exp[0]:.1f}%)', fontsize=8)
    ax_3fg.set_ylabel(f'PC2 ({var_exp[1]:.1f}%)', fontsize=8)
    ax_3fg.set_zlabel(f'PC3 ({var_exp[2]:.1f}%)', fontsize=8)
    ax_3fg.view_init(elev=25, azim=45)
    ax_3fg.tick_params(labelsize=7)

    # Panel 3h: Polar Inter-Population Phase Relationships
    ax_3h = fig.add_subplot(2, 3, 6, projection='polar')
    phases_rad = phase_data['phases_rad']
    
    for pop_name, phase_val in phases_rad.items():
        c = POP_COLORS.get(pop_name, '#333333')
        # Vector arrow from center
        ax_3h.annotate(
            '',
            xy=(phase_val, 1.0),
            xytext=(0, 0),
            arrowprops=dict(arrowstyle='->', color=c, lw=2.0)
        )
        ax_3h.plot(phase_val, 1.05, 'o', color=c, markersize=8, label=pop_name)

    ax_3h.set_title('h  Phase Relationships (Ref: V2a-1)', fontsize=11, fontweight='bold', loc='left')
    ax_3h.set_yticklabels([])
    ax_3h.set_theta_zero_location('N')
    ax_3h.set_theta_direction(-1) # Clockwise
    ax_3h.grid(True, linestyle=':', alpha=0.6)
    ax_3h.legend(loc='lower left', bbox_to_anchor=(-0.25, -0.2), ncol=3, fontsize=7, frameon=True)

    plt.tight_layout()
    fig3_path = os.path.join(output_dir, "figure3_reproduction_complete.png")
    fig.savefig(fig3_path)
    plt.close(fig)
    generated_files['figure3_complete'] = fig3_path
    print(f"Saved: {fig3_path}")

    return generated_files
