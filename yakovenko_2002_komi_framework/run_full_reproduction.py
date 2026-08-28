"""
Master Pipeline Runner: Komi et al. (2026) Framework Applied to Yakovenko et al. (2002) Data.
Executes full simulation pipeline, controls, sensitivity sweeps, and generates Figures 1-8.
"""

import sys, os
import json
import numpy as np
import pandas as pd

# Add src to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics
from phase_analysis import PhaseUnfolder
from projectome_analysis import ProjectomeAnalyzer
from traveling_wave import TravelingWaveAnalyzer
from motor_mapping import MotorOutputMapper
from gain_modulation import DecoupledGainController
from controls import ControlsAndSensitivityRunner
import figure_generators as fg


def main():
    print("================================================================================")
    print("  KOMI ET AL. (2026) FRAMEWORK APPLIED TO YAKOVENKO ET AL. (2002) DATA          ")
    print("  Cross-Paper Computational Method-Transfer & Scientific Synthesis Pipeline     ")
    print("================================================================================")

    plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # 1. Spatial Embedding
    print("\n[1/7] Embedding Yakovenko cat lumbosacral anatomy into 3D continuous geometry...")
    net = YakovenkoKomiSpatialNetwork(n_neurons=1000, rng_seed=42)
    p1 = fg.plot_fig1_spatial_mapping(net, output_dir=plots_dir)
    print(f"      [+] Generated Figure 1: {p1}")

    # 2. Connectome Construction & E/I Balancing
    print("\n[2/7] Constructing 3D anisotropic projectome & enforcing row-wise zero-sum E/I balance...")
    conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=42)
    p2 = fg.plot_fig2_connectome_balancing(conn, output_dir=plots_dir)
    print(f"      [+] Mean row sum: {conn.mean_row_sum:.2e}, Max abs: {conn.max_abs_row_sum:.2e}")
    print(f"      [+] Generated Figure 2: {p2}")

    # 3. Recurrent Rate Dynamics & Phase Unfolding
    print("\n[3/7] Integrating recurrent rate dynamics & performing PCA circular phase unfolding...")
    dyn = RecurrentRateDynamics(conn, rng_seed=42)
    times_ms, rates, currents = dyn.simulate(duration_ms=2500.0, warmup_ms=500.0)
    pu = PhaseUnfolder(rates, times_ms)
    p3 = fg.plot_fig3_dynamics_and_pca(rates, times_ms, pu, output_dir=plots_dir)
    print(f"      [+] Planar variance: {pu.planar_variance*100:.1f}%, Frequency: {pu.frequency_hz:.2f} Hz")
    print(f"      [+] Generated Figure 3: {p3}")

    # 4. Traveling Wave & Bilateral Antiphase Analysis
    print("\n[4/7] Analyzing spatiotemporal wave propagation and bilateral coordination...")
    wave = TravelingWaveAnalyzer(net, rates, times_ms)
    p4 = fg.plot_fig4_traveling_waves_bilateral(wave, output_dir=plots_dir)
    print(f"      [+] Wave velocity: {wave.velocity_mm_s:.1f} mm/s, Bilateral phase: {wave.bilateral_phase_diff_deg:.1f} deg")
    print(f"      [+] Generated Figure 4: {p4}")

    # 5. Net Projectome & Mexican-Hat Analysis
    print("\n[5/7] Quantifying emergent 1D net projectome profile and Mexican-hat index...")
    proj = ProjectomeAnalyzer(conn)
    p5 = fg.plot_fig5_net_projectome_mexican_hat(proj, output_dir=plots_dir)
    print(f"      [+] Mexican-Hat Index: {proj.mexican_hat_index:.3f}, Asymmetry (Skew): {proj.asymmetry_index:.3f}")
    print(f"      [+] Generated Figure 5: {p5}")

    # 6. Motor Output Mapping to 27 Muscles
    print("\n[6/7] Coupling recurrent dynamics to Yakovenko 27 motor pools & comparing with EMG...")
    motor = MotorOutputMapper(wave)
    print(f"      [+] Mean correlation with empirical EMG: {motor.mean_correlation:.3f}")
    print(f"      [+] Mean normalized RMSE: {motor.mean_nrmse:.3f}")

    # Decoupled Gain Modulation
    print("\n      Performing decoupled gain sweeps (sp3 amplitude vs sp2 frequency)...")
    gain_ctrl = DecoupledGainController(net)
    p6 = fg.plot_fig6_decoupled_gain_control(gain_ctrl, output_dir=plots_dir)
    print(f"      [+] Generated Figure 6: {p6}")

    # 7. Controls, Sensitivity & Cross-Paper Synthesis
    print("\n[7/7] Running benchmark controls (Controls A-D) & synthesizing cross-paper comparison...")
    runner = ControlsAndSensitivityRunner(rng_seed=42)
    controls_res = runner.run_control_experiments()
    p7 = fg.plot_fig7_controls_and_sensitivity(controls_res, output_dir=plots_dir)
    print(f"      [+] Generated Figure 7: {p7}")

    p8 = fg.plot_fig8_cross_paper_comparison(output_dir=plots_dir)
    print(f"      [+] Generated Figure 8: {p8}")

    # Export quantitative summary metrics
    summary_metrics = {
        "spatial_parameters": {
            "n_neurons": net.n_neurons,
            "length_mm": net.length_mm,
            "width_mm": net.width_mm,
            "height_mm": net.height_mm
        },
        "connectome_metrics": {
            "mean_row_sum": conn.mean_row_sum,
            "max_abs_row_sum": conn.max_abs_row_sum,
            "density": conn.density,
            "mexican_hat_index": proj.mexican_hat_index,
            "asymmetry_skew": proj.asymmetry_index
        },
        "dynamical_metrics": {
            "frequency_hz": pu.frequency_hz,
            "planar_variance": pu.planar_variance,
            "orbit_radius": pu.orbit_radius,
            "wave_velocity_mm_s": wave.velocity_mm_s,
            "bilateral_phase_diff_deg": wave.bilateral_phase_diff_deg,
            "alternation_index": wave.alternation_index
        },
        "motor_mapping_metrics": {
            "mean_correlation_with_empirical_emg": motor.mean_correlation,
            "mean_nrmse": motor.mean_nrmse
        },
        "controls_benchmarks": controls_res
    }

    json_path = os.path.join(results_dir, "komi_to_yakovenko_summary.json")
    with open(json_path, 'w') as f:
        json.dump(summary_metrics, f, indent=2)
    print(f"\n[+] Exported complete summary metrics to {json_path}")

    print("\n================================================================================")
    print("  [SUCCESS] All Komi-to-Yakovenko simulations and Figures 1-8 completed!        ")
    print("================================================================================")


if __name__ == '__main__':
    main()
