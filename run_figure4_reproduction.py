"""
Figure 4 Reproduction Script: Speed and Gait Control Experiment.
Faithfully reproduces Figure 4 of Komi et al., Nature Communications, 2026:
- Instantiates N = 5,229 mouse spinal projectome network
- Runs Walk, Trot, and Bound multi-gait simulations
- Runs continuous descending drive acceleration ramp
- Conducts descending drive parameter sweep (I_e in [15, 50] pA)
- Generates publication-quality figures for all panels 4A-4G and composite summary.
"""

import os
import sys
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from network import Network
from gait_control import (
    simulate_gait_regime,
    simulate_descending_ramp,
    run_descending_drive_sweep
)
from figure4_analysis import generate_figure4_complete


def main():
    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    print("=" * 70)
    print("REPRODUCING FIGURE 4: SPEED AND GAIT CONTROL IN SPINAL PROJECTOME")
    print("=" * 70)

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

    # 2. Multi-Gait Simulations (Walk, Trot, Bound)
    gait_results = {}
    gait_metrics_summary = {}

    print("\n2. Running physiological gait simulations...")
    for gait in ['walk', 'trot', 'bound']:
        print(f"   Simulating '{gait.upper()}' regime (10,000 ms)...")
        sim_res, metrics = simulate_gait_regime(net, gait_name=gait, t_steps=10000, seed=42)
        gait_results[gait] = (sim_res, metrics)
        gait_metrics_summary[gait] = {
            'requested_gait': metrics['gait_requested'],
            'detected_gait': metrics['gait_detected'],
            'I_e_pA': metrics['I_e'],
            'serotonin_multiplier': metrics['serotonin_mult'],
            'frequency_hz': metrics['frequency_hz'],
            'rms_amplitude_hz': metrics['rms_amplitude_hz'],
            'lr_phase_deg': metrics['lr_phase_deg'],
            'fe_phase_deg': metrics['fe_phase_deg']
        }
        print(f"   -> Detected: {metrics['gait_detected']} | Freq: {metrics['frequency_hz']:.2f} Hz | "
              f"L-R Phase: {metrics['lr_phase_deg']:.1f}° | F-E Phase: {metrics['fe_phase_deg']:.1f}°")

    # 3. Descending Drive Ramp Simulation (Acceleration)
    print("\n3. Simulating accelerating descending drive ramp (15 pA -> 50 pA over 10 s)...")
    ramp_res = simulate_descending_ramp(net, I_start=15.0, I_end=50.0, t_steps=10000, seed=42)
    print("   -> Descending ramp simulation completed.")

    # 4. Quantitative Parameter Sweep (I_e in [15, 50] pA)
    print("\n4. Running 10-point descending drive parameter sweep...")
    sweep_df = run_descending_drive_sweep(net, drive_levels=np.linspace(15.0, 50.0, 10), t_steps=4000, seed=42)
    sweep_csv_path = os.path.join(results_dir, "figure4_drive_sweep.csv")
    sweep_df.to_csv(sweep_csv_path, index=False)
    print(f"   -> Sweep results saved to {sweep_csv_path}")

    # 5. Generate All Publication Figures
    print("\n5. Generating Figure 4 publication plots...")
    generated_files = generate_figure4_complete(
        network=net,
        gait_results=gait_results,
        ramp_res=ramp_res,
        sweep_df=sweep_df,
        output_dir=plots_dir,
        dpi=300
    )

    # 6. Save Metadata & Verification Summary
    summary_path = os.path.join(results_dir, "figure4_summary.json")
    with open(summary_path, 'w') as f:
        json.dump({
            'n_neurons': net.n_neurons,
            'gaits': gait_metrics_summary,
            'generated_figures': generated_files
        }, f, indent=2)

    # 7. Save Simulation Arrays to NPZ
    npz_path = os.path.join(results_dir, "figure4_gait_results.npz")
    np.savez_compressed(
        npz_path,
        walk_rates=gait_results['walk'][0].rates,
        walk_voltage=gait_results['walk'][0].voltage,
        trot_rates=gait_results['trot'][0].rates,
        trot_voltage=gait_results['trot'][0].voltage,
        bound_rates=gait_results['bound'][0].rates,
        bound_voltage=gait_results['bound'][0].voltage,
        ramp_rates=ramp_res[0].rates,
        ramp_voltage=ramp_res[0].voltage,
        time_ms=gait_results['walk'][0].time_ms
    )

    print("\n" + "=" * 70)
    print("FIGURE 4 REPRODUCTION COMPLETE")
    print(f"Summary metrics saved to: {summary_path}")
    print(f"Timeseries arrays saved to: {npz_path}")
    for name, path in generated_files.items():
        print(f"  - [{name}]: {path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
