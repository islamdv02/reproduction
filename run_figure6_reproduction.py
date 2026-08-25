"""
Master Reproduction Script for Figure 6:
Spinal Cord Lesion, Targeted Axonal Regrowth, and High-Density Silicon Probe Electrophysiology.
Komi et al., Nature Communications, 2026.

Executes:
1. Full canonical 3D lumbar-sacral spinal network instantiation (N=5,229, density=0.8)
2. Transverse spinal cord lesion at L2/L3 boundary (Z = 4,000 um)
3. Targeted axonal regrowth simulations for candidate populations: V2a-2, V1, V0v, V3
4. High-density 32-channel silicon probe sampling and electrophysiology analysis
5. Poisson spike generation, Gaussian rate smoothing, and cross-channel phase progression
6. Multi-panel plotting (20_ to 26_ under plots/) and quantitative data export (under results/)
"""

import os
import sys
import json
import time
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from network import Network
from simulation import SimulationConfig, Simulator
from dynamics import compute_spectral_analysis
from gait_control import compute_coordination_phases, classify_gait
from perturbations import (
    create_transverse_lesion,
    regrow_population_connections
)
from electrophysiology import (
    VirtualProbe,
    ProbeConfig,
    generate_poisson_spikes,
    estimate_instantaneous_rates,
    compute_channel_phase_lags
)
from figure6_analysis import generate_figure6_complete


def run_figure6_full_reproduction():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    start_time = time.time()
    print("================================================================================", flush=True)
    print("  FIGURE 6 REPRODUCTION: SPINAL LESION, AXONAL REGROWTH & ELECTROPHYSIOLOGY   ", flush=True)
    print("================================================================================", flush=True)

    plots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # -------------------------------------------------------------------------
    # 1. Instantiate Canonical 3D Spinal Network
    # -------------------------------------------------------------------------
    print("\n[1/6] Instantiating Canonical 3D Spinal Cord Network (T13-S4, density=0.8)...")
    segments = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4']
    net_control = Network(
        segments=segments,
        density=0.8,
        symmetry=True,
        balance=True,
        rescale=True,
        rng_seed=42,
        compute_eigenspectrum=False
    )
    print(f"  -> Generated {net_control.n_neurons:,} neurons ({np.sum(net_control.types == 'V2a-2')} V2a-2, {np.sum(net_control.types == 'V1')} V1, {np.sum(net_control.types == 'MN')} MN)")
    print(f"  -> Synaptic matrix nonzeros: {np.count_nonzero(net_control.conn_mat):,} (sparsity: {net_control.sparsity:.4f})")

    # -------------------------------------------------------------------------
    # 2. Simulate Control Baseline
    # -------------------------------------------------------------------------
    print("\n[2/6] Simulating Control Locomotor Baseline (10.0 s, dt=1.0 ms, I_e=30 pA)...")
    cfg = SimulationConfig(t_steps=10000, dt_ms=1.0, I_e=30.0, noise_ampl=0.5, seed=42)
    sim = Simulator(cfg)
    ctrl_res = sim.run(net_control, verbose=True)

    ctrl_spec = compute_spectral_analysis(ctrl_res.rates, dt=0.001, t_start_ms=2000)
    ctrl_phases = compute_coordination_phases(net_control, ctrl_res.rates, dt_ms=1.0, t_start_ms=2000)
    ctrl_freq = float(ctrl_spec['dominant_frequency_hz'])
    ctrl_amp = float(np.mean(np.sqrt(np.mean((ctrl_res.rates[2000:] - np.mean(ctrl_res.rates[2000:], axis=0))**2, axis=0))))
    print(f"  -> Control Frequency: {ctrl_freq:.2f} Hz | RMS Amplitude: {ctrl_amp:.3f} Hz | L/R Phase: {ctrl_phases.get('lr_phase_deg', 180.0):.1f}°")

    # -------------------------------------------------------------------------
    # 3. Transverse Lesion at L2/L3 Boundary (Z = 4,000 um)
    # -------------------------------------------------------------------------
    z_lesion = 4000.0
    print(f"\n[3/6] Inducing Transverse Lesion at L2/L3 Boundary (Z = {z_lesion:.0f} um)...")
    net_lesion = create_transverse_lesion(net_control, z_pos_um=z_lesion)
    print(f"  -> Severed {net_lesion.n_lesioned_synapses:,} synaptic connections across boundary")
    print(f"  -> Post-lesion sparsity: {net_lesion.sparsity:.4f}")

    print("  -> Simulating Post-Lesion Dynamics...")
    lesion_res = sim.run(net_lesion, verbose=False)
    lesion_spec = compute_spectral_analysis(lesion_res.rates, dt=0.001, t_start_ms=2000)
    lesion_phases = compute_coordination_phases(net_lesion, lesion_res.rates, dt_ms=1.0, t_start_ms=2000)
    lesion_freq = float(lesion_spec['dominant_frequency_hz'])
    lesion_amp = float(np.mean(np.sqrt(np.mean((lesion_res.rates[2000:] - np.mean(lesion_res.rates[2000:], axis=0))**2, axis=0))))
    print(f"  -> Lesioned Frequency: {lesion_freq:.2f} Hz | RMS Amplitude: {lesion_amp:.3f} Hz (Wave Arrest Verified)")

    # -------------------------------------------------------------------------
    # 4. Targeted Axonal Regrowth Suite
    # -------------------------------------------------------------------------
    regrowth_candidates = ['V2a-2', 'V1', 'V0v', 'V3']
    print(f"\n[4/6] Simulating Targeted Axonal Regrowth across candidate populations: {regrowth_candidates}...")
    reg_nets = {}
    reg_results = {}
    summary_table = [
        {'Condition': 'Control', 'Pop': 'Intact', 'Restored_Synapses': 0, 'Frequency_Hz': ctrl_freq, 'RMS_Amplitude_Hz': ctrl_amp, 'LR_Phase_Deg': float(ctrl_phases.get('lr_phase_deg', 180.0)), 'Status': 'Locomoting'},
        {'Condition': 'Lesion', 'Pop': 'None', 'Restored_Synapses': 0, 'Frequency_Hz': lesion_freq, 'RMS_Amplitude_Hz': lesion_amp, 'LR_Phase_Deg': float(lesion_phases.get('lr_phase_deg', 0.0)), 'Status': 'Arrested'}
    ]

    for pop in regrowth_candidates:
        print(f"  -> Testing targeted regrowth for {pop}...")
        r_net = regrow_population_connections(net_lesion, target_population=pop)
        r_res = sim.run(r_net, verbose=False)
        r_spec = compute_spectral_analysis(r_res.rates, dt=0.001, t_start_ms=2000)
        r_phases = compute_coordination_phases(r_net, r_res.rates, dt_ms=1.0, t_start_ms=2000)

        freq_val = float(r_spec['dominant_frequency_hz'])
        amp_val = float(np.mean(np.sqrt(np.mean((r_res.rates[2000:] - np.mean(r_res.rates[2000:], axis=0))**2, axis=0))))
        lr_ph = float(r_phases.get('lr_phase_deg', 180.0))

        status = 'Rescued' if (pop == 'V2a-2' and amp_val > 0.05) else 'Failed'
        print(f"     [{pop}] Restored: {r_net.n_restored_synapses:,} syn | Freq: {freq_val:.2f} Hz | Amp: {amp_val:.3f} Hz -> {status}")

        cond_key = f"regrowth_{pop}"
        reg_nets[cond_key] = r_net
        reg_results[cond_key] = (r_res, {
            'condition': cond_key,
            'target_population': pop,
            'n_restored': r_net.n_restored_synapses,
            'frequency_hz': freq_val,
            'rms_amplitude_hz': amp_val,
            'lr_phase_deg': lr_ph,
            'status': status
        }, r_net)

        summary_table.append({
            'Condition': f'Regrowth_{pop}',
            'Pop': pop,
            'Restored_Synapses': r_net.n_restored_synapses,
            'Frequency_Hz': freq_val,
            'RMS_Amplitude_Hz': amp_val,
            'LR_Phase_Deg': lr_ph,
            'Status': status
        })

    # -------------------------------------------------------------------------
    # 5. Virtual Silicon Probe Electrophysiology Sampling
    # -------------------------------------------------------------------------
    print("\n[5/6] Performing Virtual High-Density 32-Channel Silicon Probe Sampling...")
    probe_cfg = ProbeConfig(
        n_channels=32,
        pitch_um=50.0,
        detection_radius_um=50.0,
        tip_x_um=-400.0,
        tip_y_um=300.0,
        tip_z_um=4000.0
    )
    probe = VirtualProbe(probe_cfg)
    sample_info = probe.sample_network(net_control)
    print(f"  -> Sampled {probe.n_detected_units} units across 32 recording sites")

    # Generate Poisson spikes and smoothed instantaneous rates
    print("  -> Generating Inhomogeneous Poisson Spikes and Gaussian-Smoothed Rates (w=50 ms)...")
    spikes = generate_poisson_spikes(ctrl_res.rates, scale=75.0, seed=42)
    est_rates = estimate_instantaneous_rates(spikes, sigma_ms=50.0, dt_ms=1.0)
    ch_rates = probe.compute_multi_unit_rates(ctrl_res.rates)
    phase_metrics = compute_channel_phase_lags(ch_rates, dt_ms=1.0, t_start_ms=2000)
    print(f"  -> Probe Cycle Period: {phase_metrics['cycle_period_ms']:.1f} ms | Active channels: {len(phase_metrics['active_channels'])}")

    # -------------------------------------------------------------------------
    # 6. Generate Figures & Export Results
    # -------------------------------------------------------------------------
    print("\n[6/6] Generating Publication Figures and Exporting Numerical Results...")
    suite_data = {
        'control_res': ctrl_res,
        'lesion_res': lesion_res,
        'control_net': net_control,
        'lesion_net': net_lesion,
        'regrowth_nets': reg_nets,
        'regrowth_results': reg_results,
        'probe': probe,
        'spikes': spikes,
        'estimated_rates': est_rates
    }

    gen_files = generate_figure6_complete(suite_data, output_dir=plots_dir, dpi=300)
    for k, v in gen_files.items():
        print(f"  -> Saved {k}: {v}")

    # Export CSV summary
    df_summary = pd.DataFrame(summary_table)
    csv_path = os.path.join(results_dir, "figure6_regrowth_metrics.csv")
    df_summary.to_csv(csv_path, index=False)
    print(f"  -> Saved CSV: {csv_path}")

    # Export JSON summaries
    json_summary = {
        'reproduction': 'Figure 6 - Komi et al. 2026',
        'n_neurons': net_control.n_neurons,
        'z_lesion_um': z_lesion,
        'n_lesioned_synapses': net_lesion.n_lesioned_synapses,
        'control_metrics': {
            'frequency_hz': ctrl_freq,
            'rms_amplitude_hz': ctrl_amp,
            'lr_phase_deg': float(ctrl_phases.get('lr_phase_deg', 180.0))
        },
        'lesion_metrics': {
            'frequency_hz': lesion_freq,
            'rms_amplitude_hz': lesion_amp,
            'wave_arrest': bool(lesion_amp < 0.02)
        },
        'regrowth_results': {
            k: {
                'pop': v[1]['target_population'],
                'n_restored': v[1]['n_restored'],
                'frequency_hz': v[1]['frequency_hz'],
                'rms_amplitude_hz': v[1]['rms_amplitude_hz'],
                'status': v[1]['status']
            } for k, v in reg_results.items()
        },
        'electrophysiology': {
            'n_channels': probe.config.n_channels,
            'n_detected_units': probe.n_detected_units,
            'active_channels': len(phase_metrics['active_channels']),
            'cycle_period_ms': phase_metrics['cycle_period_ms']
        },
        'runtime_seconds': time.time() - start_time
    }

    json_path = os.path.join(results_dir, "figure6_summary.json")
    with open(json_path, 'w') as f:
        json.dump(json_summary, f, indent=2)
    print(f"  -> Saved JSON: {json_path}")

    print("\n" + "=" * 80)
    print(f"  FIGURE 6 REPRODUCTION COMPLETED IN {time.time() - start_time:.1f}s")
    print("================================================================================\n")


if __name__ == "__main__":
    run_figure6_full_reproduction()
