"""
Master Reproduction Pipeline for Figure 1 of Komi et al. (Nature Communications, 2026).
Executes:
1. Balanced Sequence Generator (BSG) non-spatial simulation ($N=500$).
2. Phase-space unfolding algorithm and 1D Mexican-hat extraction.
3. 1D 5-subpopulation spatial network ($sp_1 - sp_5$) traveling wave simulation.
4. $sp_3$ gain modulation sweep (Amplitude Control).
5. $sp_2$ gain modulation sweep (Frequency Control).
6. Publication figure generation and quantitative JSON/CSV metric serialization.
"""

import os
import sys
import time
import json
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from figure1_models import (
    BSGConfig,
    BSGNetwork,
    compute_phase_unfolding,
    MexicanHat1DNetwork,
    simulate_gain_modulation_sweep
)
from figure1_analysis import (
    plot_panel_1abc_bsg_dynamics,
    plot_panel_1de_unfolded_projectome,
    plot_panel_1f_5pop_network,
    plot_panel_1g_amplitude_control,
    plot_panel_1h_frequency_control,
    plot_figure1_complete
)


def run_figure1_reproduction(output_dir: str = "plots", results_dir: str = "results") -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    start_time = time.time()

    print("=" * 80)
    print("  FIGURE 1 REPRODUCTION: BALANCED SEQUENCE GENERATION & 1D MEXICAN HAT  ")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. Non-Spatial BSG Network Simulation (Panels 1A-C)
    # -------------------------------------------------------------------------
    print("\n[1/5] Simulating Balanced Sequence Generator (BSG, N=500, p=0.1, 50% E / 50% I)...")
    bsg_cfg = BSGConfig(n_neurons=500, p_conn=0.1, prop_excitatory=0.5, t_steps=8000, dt_ms=1.0, rng_seed=42)
    bsg_net = BSGNetwork(bsg_cfg)
    bsg_sim = bsg_net.simulate()
    print(f"  -> Generated {bsg_net.n_neurons} neurons | Balanced row sum mean: {np.mean(np.sum(bsg_net.conn_mat, axis=1)):.2e}")

    # -------------------------------------------------------------------------
    # 2. Phase-Space Unfolding into 1D Mexican-Hat Projectome (Panels 1D-E)
    # -------------------------------------------------------------------------
    print("\n[2/5] Executing Phase-Space Unfolding Algorithm (ComputeFiringPhaseSorting.m)...")
    unfold_res = compute_phase_unfolding(bsg_sim['rates'], bsg_net.conn_mat, dt_ms=1.0, t_start_ms=2000)
    print(f"  -> Extracted cycle period: {unfold_res['cycle_period_ms']:.1f} ms | PC1 var: {unfold_res['explained_variance_ratio'][0]*100:.1f}%")

    # -------------------------------------------------------------------------
    # 3. 1D 5-Subpopulation Mexican-Hat Network (Panel 1F)
    # -------------------------------------------------------------------------
    print("\n[3/5] Instantiating 1D 5-Subpopulation Network (sp1-sp5, length=5000 um, N=500)...")
    net_1d = MexicanHat1DNetwork(n_neurons=500, length_um=5000.0, rng_seed=42)
    sim_1d = net_1d.simulate(t_steps=8000, dt_ms=1.0, I_e=30.0, seed=42)
    print(f"  -> Simulated 1D traveling wave along {net_1d.length_um:.0f} um cord")

    # -------------------------------------------------------------------------
    # 4. Neuromodulatory Gain Sweeps (Panels 1G & 1H)
    # -------------------------------------------------------------------------
    gain_range = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8]
    print(f"\n[4/5] Sweeping sp3 Excitatory Gain (Amplitude Control, range={gain_range})...")
    sp3_sweep = simulate_gain_modulation_sweep(net_1d, target_population='sp3', gain_levels=gain_range, seed=42)
    print(f"  -> Amplitude change: {sp3_sweep['amplitudes_hz'][0]:.3f} Hz -> {sp3_sweep['amplitudes_hz'][-1]:.3f} Hz | Freq change: {sp3_sweep['frequencies_hz'][0]:.2f} Hz -> {sp3_sweep['frequencies_hz'][-1]:.2f} Hz")

    print(f"\n[5/5] Sweeping sp2 Inhibitory Gain (Frequency Control, range={gain_range})...")
    sp2_sweep = simulate_gain_modulation_sweep(net_1d, target_population='sp2', gain_levels=gain_range, seed=42)
    print(f"  -> Freq change: {sp2_sweep['frequencies_hz'][0]:.2f} Hz -> {sp2_sweep['frequencies_hz'][-1]:.2f} Hz | Amplitude change: {sp2_sweep['amplitudes_hz'][0]:.3f} Hz -> {sp2_sweep['amplitudes_hz'][-1]:.3f} Hz")

    # -------------------------------------------------------------------------
    # 5. Plotting & Exporting Artifacts
    # -------------------------------------------------------------------------
    print("\n[6/6] Generating Publication Figures and Exporting Metrics...")

    p_1abc = os.path.join(output_dir, "01_fig1abc_bsg_dynamics.png")
    fig_1abc = plot_panel_1abc_bsg_dynamics(bsg_net, bsg_sim, unfold_res, output_path=p_1abc, dpi=300)
    plt.close(fig_1abc)

    p_1de = os.path.join(output_dir, "02_fig1de_unfolded_projectome.png")
    fig_1de = plot_panel_1de_unfolded_projectome(unfold_res, output_path=p_1de, dpi=300)
    plt.close(fig_1de)

    p_1f = os.path.join(output_dir, "03_fig1f_5pop_network.png")
    fig_1f = plot_panel_1f_5pop_network(net_1d, sim_1d, output_path=p_1f, dpi=300)
    plt.close(fig_1f)

    p_1g = os.path.join(output_dir, "04_fig1g_amplitude_control.png")
    fig_1g = plot_panel_1g_amplitude_control(sp3_sweep, output_path=p_1g, dpi=300)
    plt.close(fig_1g)

    p_1h = os.path.join(output_dir, "05_fig1h_frequency_control.png")
    fig_1h = plot_panel_1h_frequency_control(sp2_sweep, output_path=p_1h, dpi=300)
    plt.close(fig_1h)

    p_comp = os.path.join(output_dir, "figure1_complete.png")
    bsg_data = {'unfold_res': unfold_res}
    model1d_data = {'net_1d': net_1d, 'sim_res': sim_1d}
    fig_comp = plot_figure1_complete(bsg_data, model1d_data, sp3_sweep, sp2_sweep, output_path=p_comp, dpi=300)
    plt.close(fig_comp)

    # Export CSVs and JSON summaries
    df_sp3 = pd.DataFrame({
        'gain_sp3': sp3_sweep['gain_levels'],
        'amplitude_rms_hz': sp3_sweep['amplitudes_hz'],
        'frequency_hz': sp3_sweep['frequencies_hz'],
        'orbit_radius': sp3_sweep['orbit_radii']
    })
    p_csv_sp3 = os.path.join(results_dir, "figure1_sp3_amplitude_sweep.csv")
    df_sp3.to_csv(p_csv_sp3, index=False)

    df_sp2 = pd.DataFrame({
        'gain_sp2': sp2_sweep['gain_levels'],
        'frequency_hz': sp2_sweep['frequencies_hz'],
        'amplitude_rms_hz': sp2_sweep['amplitudes_hz'],
        'orbit_radius': sp2_sweep['orbit_radii']
    })
    p_csv_sp2 = os.path.join(results_dir, "figure1_sp2_frequency_sweep.csv")
    df_sp2.to_csv(p_csv_sp2, index=False)

    summary_metrics = {
        'figure': 1,
        'title': 'Balanced Sequence Generation, Mexican-Hat Projectomes, and Decoupled Motor Control',
        'bsg_model': {
            'n_neurons': bsg_net.n_neurons,
            'p_conn': bsg_cfg.p_conn,
            'cycle_period_ms': unfold_res['cycle_period_ms'],
            'pc1_explained_var': float(unfold_res['explained_variance_ratio'][0]),
            'pc2_explained_var': float(unfold_res['explained_variance_ratio'][1])
        },
        'sp3_amplitude_control': {
            'target_population': 'sp3 (Excitatory)',
            'gain_min': float(gain_range[0]),
            'gain_max': float(gain_range[-1]),
            'amplitude_min': float(sp3_sweep['amplitudes_hz'][0]),
            'amplitude_max': float(sp3_sweep['amplitudes_hz'][-1]),
            'amplitude_scaling_factor': float(sp3_sweep['amplitudes_hz'][-1] / max(1e-6, sp3_sweep['amplitudes_hz'][0])),
            'frequency_delta_percent': float(abs(sp3_sweep['frequencies_hz'][-1] - sp3_sweep['frequencies_hz'][0]) / sp3_sweep['frequencies_hz'][0] * 100)
        },
        'sp2_frequency_control': {
            'target_population': 'sp2 (Inhibitory)',
            'gain_min': float(gain_range[0]),
            'gain_max': float(gain_range[-1]),
            'frequency_min': float(sp2_sweep['frequencies_hz'][0]),
            'frequency_max': float(sp2_sweep['frequencies_hz'][-1]),
            'frequency_scaling_factor': float(sp2_sweep['frequencies_hz'][-1] / max(1e-6, sp2_sweep['frequencies_hz'][0])),
            'amplitude_delta_percent': float(abs(sp2_sweep['amplitudes_hz'][-1] - sp2_sweep['amplitudes_hz'][0]) / sp2_sweep['amplitudes_hz'][0] * 100)
        },
        'artifacts': {
            'panel_1abc': p_1abc,
            'panel_1de': p_1de,
            'panel_1f': p_1f,
            'panel_1g': p_1g,
            'panel_1h': p_1h,
            'figure1_complete': p_comp,
            'csv_sp3': p_csv_sp3,
            'csv_sp2': p_csv_sp2
        }
    }

    p_json = os.path.join(results_dir, "figure1_summary.json")
    with open(p_json, 'w') as f:
        json.dump(summary_metrics, f, indent=2)

    elapsed = time.time() - start_time
    print(f"\n{'=' * 80}")
    print(f"  FIGURE 1 REPRODUCTION COMPLETED IN {elapsed:.1f}s")
    print(f"{'=' * 80}\n")
    return summary_metrics


if __name__ == '__main__':
    run_figure1_reproduction()
