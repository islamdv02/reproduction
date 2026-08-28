"""
Master Critical Validation Runner: Komi et al. (2026) Applied to Yakovenko et al. (2002).
Orchestrates parameter provenance, 11 ablations, parameter sweeps, 10-seed Monte Carlo, wave math, and 10 figures.
"""

import sys, os
import json
import numpy as np
import pandas as pd

# Path setup
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from model_y import ModelY
from model_ky import ModelKY
from parameter_provenance_builder import build_parameter_provenance_table
from ablation_experiments import AblationEngine
from parameter_sensitivity_suite import ParameterSensitivitySuite
from critical_monte_carlo import CriticalMonteCarloEvaluator
from wave_comparative_math import build_wave_definition_table
import critical_figures as cf


def main():
    print("================================================================================")
    print("  CRITICAL SCIENTIFIC VALIDATION: KOMI ET AL. (2026) & YAKOVENKO ET AL. (2002)   ")
    print("  Unbiased Mechanistic Investigation, Parameter Provenance & 11 Ablations       ")
    print("================================================================================")

    plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # 1. Parameter Provenance Audit
    print("\n[1/6] Building Parameter Provenance Audit...")
    prov_df = build_parameter_provenance_table()
    prov_csv = os.path.join(results_dir, "parameter_provenance.csv")
    prov_df.to_csv(prov_csv, index=False)
    print(f"      [+] Exported parameter provenance table to {prov_csv}")

    # 2. 11 Systematic Ablation Experiments (Conditions A through K)
    print("\n[2/6] Executing 11 Systematic Ablation Experiments (Conditions A through K)...")
    ablation_engine = AblationEngine(rng_seed=42, n_neurons=800)
    ablation_df = ablation_engine.run_all_11_ablations()
    ablation_csv = os.path.join(results_dir, "ablation_results.csv")
    ablation_df.to_csv(ablation_csv, index=False)
    print(f"      [+] Exported ablation benchmark results to {ablation_csv}")

    # 3. Parameter Sensitivity Sweeps
    print("\n[3/6] Running Parameter Sensitivity Sweeps (mu_z, sigma_z, tau, I_tonic, comm_frac)...")
    sensitivity_runner = ParameterSensitivitySuite(rng_seed=42, n_neurons=600)
    sensitivity_df = sensitivity_runner.run_all_sweeps()
    sens_csv = os.path.join(results_dir, "parameter_sensitivity.csv")
    sensitivity_df.to_csv(sens_csv, index=False)
    print(f"      [+] Exported parameter sensitivity results to {sens_csv}")

    # 4. Multi-Seed Robustness & Monte Carlo Evaluation (N=10 seeds)
    print("\n[4/6] Running 10-Seed Monte Carlo Robustness Evaluation...")
    mc_runner = CriticalMonteCarloEvaluator(seeds=[42, 101, 2024, 7, 99, 1234, 555, 888, 314, 777])
    mc_df, mc_stats = mc_runner.run_10_seed_evaluation()
    mc_csv = os.path.join(results_dir, "critical_validation_metrics.csv")
    mc_json = os.path.join(results_dir, "critical_validation_metrics.json")
    mc_df.to_csv(mc_csv, index=False)
    with open(mc_json, 'w') as f:
        json.dump(mc_stats, f, indent=2)
    print(f"      [+] Exported 10-seed metrics to {mc_csv} and {mc_json}")

    # 5. Wave Definition Comparison Table
    print("\n[5/6] Building Wave Definition & Mathematical Mechanism Comparison Table...")
    wave_df = build_wave_definition_table()
    wave_csv = os.path.join(results_dir, "wave_definition_comparison.csv")
    wave_df.to_csv(wave_csv, index=False)
    print(f"      [+] Exported wave definition comparison to {wave_csv}")

    # 6. Generate 10 Publication-Quality Figures
    print("\n[6/6] Generating Figures 1 through 10...")
    model_y = ModelY(recruitment_mode='graded', n_cycles=2)
    model_ky = ModelKY(n_neurons=800, rng_seed=42, duration_ms=2500.0, warmup_ms=500.0)
    cf.generate_all_10_figures(
        model_y=model_y,
        model_ky=model_ky,
        ablation_df=ablation_df,
        sensitivity_df=sensitivity_df,
        monte_carlo_df=mc_df,
        wave_def_df=wave_df,
        output_dir=plots_dir
    )
    print(f"      [+] Generated Figures 1-10 in {plots_dir}")

    print("\n================================================================================")
    print("  [SUCCESS] All critical validation tasks completed cleanly and robustly!       ")
    print("================================================================================")


if __name__ == '__main__':
    main()
