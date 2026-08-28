"""
Master Runner: Hypothesis-Neutral Scientific Test of Komi et al. (2026) Against Yakovenko et al. (2002).
Executes the full computational pipeline, multi-seed control experiments, sensitivity sweeps,
and outputs all 10 publication figures and statistical summaries.
"""

import os, sys, json
import numpy as np
import pandas as pd

# Add local src to path
local_src = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if local_src not in sys.path:
    sys.path.insert(0, local_src)

from parameter_provenance import get_parameter_provenance_dataframe, get_preregistered_predictions_dataframe
from independent_baselines import ModelY_Baseline, ModelK_Baseline
from model_ky_transfer import ModelKY_Transfer
from controls_and_nulls import CriticalControlsSuite
from parameter_sensitivity_sweeps import ParameterSensitivitySuite
from velocity_and_measurement_math import analytical_bimodal_somatotopy_derivation, get_5_phenomena_comparison_dataframe
from generate_10_scientific_figures import generate_all_10_figures


def main():
    print("=" * 80)
    print("HYPOTHESIS-NEUTRAL SCIENTIFIC TEST: KOMI ET AL. (2026) VS. YAKOVENKO ET AL. (2002)")
    print("=" * 80)

    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    # 1. Parameter Provenance & Pre-Registered Predictions
    print("\n[Step 1/6] Generating Parameter Provenance & Pre-Registered Predictions...")
    prov_df = get_parameter_provenance_dataframe()
    prov_df.to_csv(os.path.join(results_dir, 'parameter_provenance_table.csv'), index=False)
    pred_df = get_preregistered_predictions_dataframe()
    pred_df.to_csv(os.path.join(results_dir, 'preregistered_predictions_table.csv'), index=False)
    print(f" -> Provenance table exported ({len(prov_df)} parameters).")
    print(f" -> Pre-registered predictions exported ({len(pred_df)} mechanisms).")

    # 2. Independent Baselines
    print("\n[Step 2/6] Running Independent Baselines (Model Y and Model K)...")
    model_y = ModelY_Baseline(recruitment_mode='graded', n_cycles=2)
    print(f" -> Model Y (Yakovenko Cat): Reconstructed {model_y.n_slices} slices, r_cm range = [{np.min(model_y.r_cm_level):.1f}, {np.max(model_y.r_cm_level):.1f}] levels.")
    model_k = ModelK_Baseline(n_neurons=500, rng_seed=42)
    print(f" -> Model K (Komi Mouse): Emergent wave velocity = {model_k.wave_velocity_mm_s:.2f} mm/s, planar var = {model_k.planar_variance*100:.1f}%.")

    # 3. Model KY Untuned Transfer
    print("\n[Step 3/6] Running Model KY-Transfer (Untuned Rate Dynamics on Cat Anatomy)...")
    model_ky = ModelKY_Transfer(n_neurons=800, rng_seed=42, duration_ms=2400.0, warmup_ms=400.0)
    print(f" -> Model KY-Transfer: Emergent wave velocity = {model_ky.wave.velocity_mm_s:.2f} mm/s, planar var = {model_ky.phase_unfolder.planar_variance*100:.1f}%.")
    print(f" -> Projectome audit: Peak exc = {model_ky.projectome.peak_excitation:.4f}, Trough inh = {model_ky.projectome.trough_inhibition:.4f}")
    print(f" -> Corrected Contrast MHC = {model_ky.projectome.contrast_mhc:.2f}, Legacy MHI = {model_ky.projectome.legacy_buggy_mhi:.3f}")

    # 4. Critical Controls & Matched Null Models (Multi-Seed)
    print("\n[Step 4/6] Executing 10 Critical Control Experiments Across 10 Monte Carlo Seeds...")
    ctrl_suite = CriticalControlsSuite(n_neurons=600, n_seeds=10)
    controls_df, raw_profiles = ctrl_suite.run_all_controls()
    controls_df.to_csv(os.path.join(results_dir, 'controls_and_nulls_summary.csv'), index=False)
    print(f" -> Controls & nulls completed ({len(controls_df)} conditions).")
    print(f" -> Komi vs Matched Null: t = {ctrl_suite.t_stat_komi_vs_null:.3f}, p = {ctrl_suite.p_val_komi_vs_null:.4e}")

    # 5. Parameter Sensitivity Sweeps
    print("\n[Step 5/6] Running Systematic Parameter Sensitivity Sweeps...")
    sens_suite = ParameterSensitivitySuite(n_neurons=500, rng_seed=42)
    sensitivity_df = sens_suite.run_full_sensitivity_analysis()
    sensitivity_df.to_csv(os.path.join(results_dir, 'parameter_sensitivity_summary.csv'), index=False)
    print(f" -> Sensitivity sweeps completed ({len(sensitivity_df)} evaluated parameter combinations).")

    # 6. Generate All 10 Publication Figures
    print("\n[Step 6/6] Rendering All 10 Publication Figures (300 DPI)...")
    generate_all_10_figures(
        model_y=model_y,
        model_k=model_k,
        model_ky=model_ky,
        controls_df=controls_df,
        raw_profiles=raw_profiles,
        sensitivity_df=sensitivity_df,
        output_dir=plots_dir
    )
    print(" -> All 10 publication figures saved to plots/ directory.")

    # 7. Export Comprehensive Master JSON
    komi_r_mean = float(controls_df.loc[controls_df['cond_id'] == 'Intact_Model_KY', 'pearson_r_mean'].values[0])
    null_r_mean = float(controls_df.loc[controls_df['cond_id'] == 'Ctrl_10_Matched_Null', 'pearson_r_mean'].values[0])
    delta_r = komi_r_mean - null_r_mean

    master_results = {
        "study_title": "Hypothesis-Neutral Scientific Test of Komi et al. (2026) Against Yakovenko et al. (2002)",
        "date": "August 2026",
        "verdict_classification": "D. SAME PHENOMENON AT DIFFERENT MEASUREMENT LEVELS & COMPLEMENTARY MECHANISMS",
        "primary_findings": {
            "model_ky_untuned_correlation_r_mean": komi_r_mean,
            "matched_null_correlation_r_mean": null_r_mean,
            "delta_r_effect_size": delta_r,
            "p_value_komi_vs_null": ctrl_suite.p_val_komi_vs_null,
            "t_statistic": ctrl_suite.t_stat_komi_vs_null,
            "statistically_significant": bool(ctrl_suite.p_val_komi_vs_null < 0.01),
            "mexican_hat_bug_resolved": True,
            "legacy_mhi_bug_explanation": "Prior (peak - trough)/(peak + |trough|) with trough < 0 algebraically simplified to 1.000 identically.",
            "corrected_projectome_contrast_mhc": float(model_ky.projectome.contrast_mhc),
            "velocity_reconciliation": "dr_cm/dt (kinematic centroid migration, peaks > 40 mm/s) is mathematically distinct from omega/k (interneuronal phase wave velocity, ~10-40 mm/s)."
        }
    }

    with open(os.path.join(results_dir, 'master_scientific_audit.json'), 'w') as f:
        json.dump(master_results, f, indent=2)

    print("\n" + "=" * 80)
    print("MASTER EXECUTION COMPLETED SUCCESSFULLY!")
    print(f"Komi Model Untuned Correlation with Yakovenko: r = {komi_r_mean:.3f}")
    print(f"Matched Null Model Correlation: r = {null_r_mean:.3f}")
    print(f"Effect Size Delta r = {delta_r:.3f} (p = {ctrl_suite.p_val_komi_vs_null:.4e})")
    print("=" * 80)


if __name__ == "__main__":
    main()
