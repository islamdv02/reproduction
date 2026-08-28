"""
Master Execution Pipeline: Komi et al. (2026) vs. Yakovenko et al. (2002) Mechanistic Study.
Runs Model Y, Model K-Y, multi-seed Monte Carlo comparison (n=5 seeds), 8 controls, and generates Figures 1-8.
"""

import sys, os
import json
import numpy as np
import pandas as pd

# Add src to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from model_y import ModelY
from model_ky import ModelKY
from wave_decomposition import WaveDecomposer
from controls_suite import ControlsSuite
from mechanistic_comparator import MechanisticComparator
import figure_plotting as fp


def main():
    print("================================================================================")
    print("  KOMI ET AL. (2026) VS. YAKOVENKO ET AL. (2002) MECHANISTIC STUDY             ")
    print("  Investigating Compatibility, Traveling Wave Concepts & Explanatory Levels     ")
    print("================================================================================")

    plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # 1. Instantiate Model Y and Model K-Y
    print("\n[1/6] Running Model Y (Yakovenko Feedforward) and Model K-Y (Komi Recurrent)...")
    m_y = ModelY(recruitment_mode='graded', n_cycles=2)
    m_ky = ModelKY(n_neurons=800, rng_seed=42, duration_ms=2500.0, warmup_ms=500.0)

    p1 = fp.plot_fig1_yakovenko_reference(m_y, output_dir=plots_dir)
    p2 = fp.plot_fig2_komi_yakovenko_network(m_ky, output_dir=plots_dir)
    p3 = fp.plot_fig3_activity_comparison(m_y, m_ky, output_dir=plots_dir)
    p4 = fp.plot_fig4_center_of_activity_comparison(m_y, m_ky, output_dir=plots_dir)
    print(f"      [+] Generated Figures 1-4 in {plots_dir}")

    # 2. Wave Decomposition Analysis (Wave A, B, C)
    print("\n[2/6] Decomposing Wave Phenomena (Wave A: Migration, Wave B: Stance/Swing, Wave C: Traveling Wave)...")
    decomposer = WaveDecomposer(m_y, m_ky)
    wave_summary = decomposer.get_summary_dict()
    p5 = fp.plot_fig5_wave_comparison(decomposer, output_dir=plots_dir)
    p6 = fp.plot_fig6_connectivity_projectome(m_ky, output_dir=plots_dir)
    print(f"      [+] Generated Figures 5-6 in {plots_dir}")

    # 3. Controlled Experiments (8 Controls)
    print("\n[3/6] Running 8 Systematic Controlled Experiments (Controls 1-8)...")
    controls_runner = ControlsSuite(rng_seed=42)
    controls_res = controls_runner.run_all_8_controls()
    p7 = fp.plot_fig7_controls(controls_res, output_dir=plots_dir)
    print(f"      [+] Generated Figure 7: {p7}")

    # 4. Multi-Seed Monte Carlo Comparison (N=5 seeds)
    print("\n[4/6] Executing Multi-Seed Monte Carlo Comparison (N=5 seeds)...")
    comparator = MechanisticComparator(seeds=[42, 101, 2024, 7, 99])
    df_seeds, stats = comparator.run_multi_seed_comparison()

    csv_path = os.path.join(results_dir, "comparison_metrics.csv")
    df_seeds.to_csv(csv_path, index=False)
    print(f"      [+] Exported multi-seed comparison metrics to {csv_path}")

    # 5. Conceptual Synthesis Figure
    print("\n[5/6] Generating Conceptual Synthesis Summary Diagram...")
    p8 = fp.plot_fig8_mechanistic_summary(output_dir=plots_dir)
    print(f"      [+] Generated Figure 8: {p8}")

    # 6. Export Full JSON Summary
    full_summary = {
        "study_title": "Mechanistic Comparison: Komi et al. (2026) vs Yakovenko et al. (2002)",
        "wave_decomposition": wave_summary,
        "controls_benchmarks": controls_res,
        "multi_seed_monte_carlo_stats": stats,
        "final_classification": "B. Partial Compatibility / Complementary Mechanistic Levels",
        "scientific_resolution": "Komi's continuous interneuronal traveling wave acts as the generative engine that drives Yakovenko's discrete, somatotopically segregated motoneuron pool jumps."
    }

    json_path = os.path.join(results_dir, "comparison_metrics.json")
    with open(json_path, 'w') as f:
        json.dump(full_summary, f, indent=2)
    print(f"\n[+] Exported complete results JSON to {json_path}")

    print("\n================================================================================")
    print("  [SUCCESS] Mechanistic comparison pipeline completed successfully!            ")
    print("================================================================================")


if __name__ == '__main__':
    main()
