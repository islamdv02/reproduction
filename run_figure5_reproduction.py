"""
Figure 5 Reproduction Script: Cell-Type Perturbation Experiments.
Faithfully reproduces Figure 5 of Komi et al., Nature Communications, 2026:
- Instantiates N = 5,229 mouse spinal projectome network (T13-S4, D=0.8, seed 42)
- Runs 10-second simulations for Control, V1 ablation, and V0 ablation
- Quantifies frequency, amplitude, Left-Right phase, and Flexor-Extensor phase
- Generates publication-quality figures for panels 5A-5F and composite Figure 5
- Exports summary metrics to JSON and simulation timeseries to NPZ.
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
from perturbations import run_figure5_perturbation_suite
from figure5_analysis import generate_figure5_complete


def main():
    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    print("=" * 70)
    print("REPRODUCING FIGURE 5: CELL-TYPE PERTURBATION EXPERIMENTS")
    print("=" * 70)

    # 1. Instantiate baseline spinal projectome network (N = 5,229)
    print("\n1. Instantiating baseline spinal network (T13-S4, D=0.8, seed 42)...")
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
    print(f"   Baseline network instantiated with N = {net.n_neurons} neurons.")

    # 2. Run Figure 5 perturbation suite (Control, V1, V0)
    print("\n2. Running 10-second simulations for Control, V1 Ablation, V0 Ablation...")
    suite_results = run_figure5_perturbation_suite(
        network=net,
        perturbation_mode="ablation",
        t_steps=10000,
        seed=42
    )

    summary_metrics = {}
    for cond_name, (res, metrics, active_net) in suite_results.items():
        print(f"   [{cond_name.upper()}] Freq: {metrics['frequency_hz']:.2f} Hz | "
              f"RMS Amp: {metrics['rms_amplitude_hz']:.3f} | "
              f"L-R Phase: {metrics['lr_phase_deg']:.1f}° | "
              f"F-E Phase: {metrics['fe_phase_deg']:.1f}° | "
              f"Gait: {metrics['gait_detected']}")
        summary_metrics[cond_name] = metrics

    # 3. Generate all Figure 5 publication panels
    print("\n3. Generating Figure 5 publication figures...")
    generated_files = generate_figure5_complete(
        suite_results=suite_results,
        output_dir=plots_dir,
        dpi=300
    )

    # 4. Save metadata summary
    summary_path = os.path.join(results_dir, "figure5_summary.json")
    with open(summary_path, 'w') as f:
        json.dump({
            'n_neurons': net.n_neurons,
            'conditions': summary_metrics,
            'generated_figures': generated_files
        }, f, indent=2)

    # 5. Save timeseries arrays to NPZ
    npz_path = os.path.join(results_dir, "figure5_perturbation_results.npz")
    np.savez_compressed(
        npz_path,
        control_rates=suite_results['control'][0].rates,
        control_voltage=suite_results['control'][0].voltage,
        v1_rates=suite_results['v1'][0].rates,
        v1_voltage=suite_results['v1'][0].voltage,
        v0_rates=suite_results['v0'][0].rates,
        v0_voltage=suite_results['v0'][0].voltage,
        time_ms=suite_results['control'][0].time_ms
    )

    print("\n" + "=" * 70)
    print("FIGURE 5 REPRODUCTION COMPLETE")
    print(f"Summary metrics saved to: {summary_path}")
    print(f"Timeseries arrays saved to: {npz_path}")
    for name, path in generated_files.items():
        print(f"  - [{name}]: {path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
