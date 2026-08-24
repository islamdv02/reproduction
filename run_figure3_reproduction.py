"""
Figure 3 Reproduction Script: Normal Locomotion Experiment.
Executes the normal locomotion simulation and generates high-resolution
publication figures for Figure 3 of Komi et al., Nature Communications, 2026.
"""

import os
import sys
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from network import Network
from simulation import SimulationConfig, Simulator, SimulationResult
from locomotion import (
    generate_synthetic_emg,
    compute_traveling_wave,
    compute_pca_dynamics,
    compute_population_phases,
    generate_poisson_spikes_and_rates,
    MUSCLE_FLEX_EXT
)
from figure3_analysis import generate_figure3_complete, POP_COLORS, MUSCLE_COLORS


def main():
    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    print("=" * 65)
    print("REPRODUCING FIGURE 3: NORMAL LOCOMOTION IN SPINAL PROJECTOME MODEL")
    print("=" * 65)

    # 1. Instantiate full spinal projectome network (N = 5,229)
    print("\n1. Instantiating spinal projectome network (T13-S4, D=0.8)...")
    segments = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4']
    net = Network(
        segments=segments,
        density=0.8,
        symmetry=True,
        balance=True,
        rescale=True,
        rng_seed=42,
        compute_eigenspectrum=False
    )
    print(f"Network instantiated with N = {net.n_neurons} neurons.")

    # 2. Check if baseline simulation exists or run
    ckpt_path = os.path.join(results_dir, "baseline_simulation_results.npz")
    if os.path.exists(ckpt_path):
        print(f"\n2. Loading existing baseline simulation from {ckpt_path}...")
        data = np.load(ckpt_path, allow_pickle=True)
        time_ms = data['time_ms']
        rates = data['rates']
        voltage = data['voltage']
        
        # Reconstruct population rates
        pop_rates = {}
        for pop_name in POP_COLORS.keys():
            mask = (net.types == pop_name)
            if np.any(mask):
                pop_rates[pop_name] = np.mean(rates[:, mask], axis=1)
                
        sim_res = SimulationResult(
            config=SimulationConfig(),
            time_ms=time_ms,
            rates=rates,
            voltage=voltage,
            population_rates=pop_rates,
            spectral_analysis={},
            final_voltage=voltage[-1, :],
            final_rates=rates[-1, :]
        )
    else:
        print("\n2. Executing 10,000 ms baseline simulation...")
        cfg = SimulationConfig(t_steps=10000, dt_ms=1.0, tau_V_ms=50.0, I_e=30.0, seed=5)
        sim = Simulator(cfg)
        sim_res = sim.run(net, verbose=True)
        sim_res.save_checkpoint(results_dir, prefix="baseline_simulation")

    # 3. Generate Complete Multi-Panel Figure 3
    print("\n3. Generating unified multi-panel Figure 3...")
    gen_files = generate_figure3_complete(
        network=net,
        sim_result=sim_res,
        output_dir=plots_dir,
        dpi=300
    )

    # 4. Generate Individual High-Resolution Panels for Figure 3
    print("\n4. Generating individual panel figures...")
    t_zoom_mask = (sim_res.time_ms >= 1000) & (sim_res.time_ms <= 3000)
    t_zoom = sim_res.time_ms[t_zoom_mask]

    emg_data = generate_synthetic_emg(
        rates=sim_res.rates,
        neuron_types=net.types,
        neuron_lat=net.pos_x,
        neuron_z=net.pos_z,
        time_ms=sim_res.time_ms,
        noise_level=0.15,
        window_ms=20,
        rng_seed=42
    )

    wave_data = compute_traveling_wave(
        rates=sim_res.rates,
        neuron_z=net.pos_z,
        dt_ms=1.0,
        t_start_ms=1000,
        n_spatial_bins=20
    )

    pca_data = compute_pca_dynamics(
        rates=sim_res.rates,
        n_components=3,
        t_start_ms=1000
    )

    phase_data = compute_population_phases(
        population_rates=sim_res.population_rates,
        dt_ms=1.0,
        t_start_ms=1000,
        reference_pop='V2a-1'
    )

    # Save Bilateral EMG comparison
    fig, (ax_r, ax_l) = plt.subplots(1, 2, figsize=(15, 7), dpi=300, sharey=True)
    for ax, side in [(ax_r, 'Right'), (ax_l, 'Left')]:
        s_emg = emg_data[side]
        muscles = s_emg['muscles']
        envs = s_emg['envelope'][t_zoom_mask, :]
        flex_ext = s_emg['flex_ext']
        
        for (t_start, t_end) in s_emg['stance_swing_bounds']:
            if t_end >= t_zoom[0] and t_start <= t_zoom[-1]:
                ax.axvspan(max(t_start, t_zoom[0]), min(t_end, t_zoom[-1]), color='#e0e0e0', alpha=0.5, lw=0)

        for m_i, m_name in enumerate(muscles):
            c = MUSCLE_COLORS[flex_ext[m_i]]
            offset = (len(muscles) - 1 - m_i) * 35.0
            ax.plot(t_zoom, envs[:, m_i] + offset, color=c, linewidth=1.6)
            ax.text(t_zoom[0] - 20, offset + 8, f"{m_name} ({flex_ext[m_i]})", ha='right', va='center', fontsize=8, fontweight='bold', color=c)
            
        ax.set_title(f'{side} Hemichord Hindlimb EMG', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (ms)', fontsize=11)
        ax.set_yticks([])
        ax.set_xlim(t_zoom[0] - 150, t_zoom[-1] + 20)
        ax.grid(True, linestyle=':', alpha=0.3, axis='x')

    plt.tight_layout()
    p_emg = os.path.join(plots_dir, "figure3_panel_3d_emg_bilateral.png")
    fig.savefig(p_emg)
    plt.close(fig)
    print(f"Saved: {p_emg}")

    # 5. Export Quantitative Metrics
    metrics = {
        "network_size": net.n_neurons,
        "locomotor_frequency_hz": wave_data['loco_frequency_hz'],
        "cycle_period_ms": wave_data['cycle_period_ms'],
        "traveling_wave_velocity_mm_s": wave_data['wave_velocity_mm_s'],
        "traveling_wave_r_squared": wave_data['r_squared'],
        "pca_variance_explained_top3": float(pca_data['cumulative_variance'][2]),
        "pca_variance_pc1": float(pca_data['explained_variance_ratio'][0]),
        "pca_variance_pc2": float(pca_data['explained_variance_ratio'][1]),
        "pca_variance_pc3": float(pca_data['explained_variance_ratio'][2]),
        "population_phases_deg": phase_data['phases_deg']
    }

    metrics_path = os.path.join(results_dir, "figure3_reproduction_metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved quantitative metrics to {metrics_path}")

    print("\n--- Figure 3 Quantitative Results ---")
    print(f"Locomotor Frequency       : {metrics['locomotor_frequency_hz']:.2f} Hz (Period: {metrics['cycle_period_ms']:.1f} ms)")
    print(f"Traveling Wave Velocity   : {metrics['traveling_wave_velocity_mm_s']:.2f} mm/s (R² = {metrics['traveling_wave_r_squared']:.3f})")
    print(f"PCA Top 3 PCs Variance    : {metrics['pca_variance_explained_top3']*100:.1f}% (PC1: {metrics['pca_variance_pc1']*100:.1f}%, PC2: {metrics['pca_variance_pc2']*100:.1f}%, PC3: {metrics['pca_variance_pc3']*100:.1f}%)")
    print(f"Population Phases (rel to V2a-1):")
    for pop, deg in metrics['population_phases_deg'].items():
        print(f"  {pop:8s}: {deg:6.1f}°")
    print("=" * 65)


if __name__ == "__main__":
    main()
