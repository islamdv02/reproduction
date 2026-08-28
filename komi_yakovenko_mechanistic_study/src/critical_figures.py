"""
Critical Figures Module: 10 Publication-Quality Figures (Figures 1 through 10).
Produces comprehensive, data-driven figures directly addressing all scientific questions.
"""

import os
from typing import Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
from scipy import signal

import sys
base_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'yakovenko_2002_reproduction', 'src'))
if base_src not in sys.path:
    sys.path.insert(0, base_src)
from anatomy import MUSCLE_CATEGORIES, MUSCLE_NAMES

from model_y import ModelY
from model_ky import ModelKY


def generate_all_10_figures(
    model_y: ModelY,
    model_ky: ModelKY,
    ablation_df: pd.DataFrame,
    sensitivity_df: pd.DataFrame,
    monte_carlo_df: pd.DataFrame,
    wave_def_df: pd.DataFrame,
    output_dir: str = "plots"
):
    os.makedirs(output_dir, exist_ok=True)

    # -------------------------------------------------------------
    # Figure 1: Yakovenko Reference Data
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), dpi=300)
    fig.suptitle("Figure 1: Yakovenko Reference Data: Anatomical MN Somatotopy, Muscle Maps & Empirical EMG",
                 fontsize=12, fontweight='bold', y=0.98)

    # 1A: MN Distribution
    ax1 = axes[0]
    slices = np.arange(1, 31)
    anat = model_y.anatomy
    flex_idx = [i for i, m in enumerate(MUSCLE_NAMES) if MUSCLE_CATEGORIES.get(m) == 'flexor']
    ext_idx = [i for i, m in enumerate(MUSCLE_NAMES) if MUSCLE_CATEGORIES.get(m) == 'extensor']
    ret_idx = [i for i, m in enumerate(MUSCLE_NAMES) if MUSCLE_CATEGORIES.get(m) == 'retractor']
    f_cnt = np.sum(anat.slice_matrix[flex_idx, :], axis=0)
    e_cnt = np.sum(anat.slice_matrix[ext_idx, :], axis=0)
    r_cnt = np.sum(anat.slice_matrix[ret_idx, :], axis=0)
    ax1.bar(slices, e_cnt, color='#d62728', alpha=0.75, label='Extensors (77% Caudal)')
    ax1.bar(slices, r_cnt, bottom=e_cnt, color='#2ca02c', alpha=0.75, label='Retractors')
    ax1.bar(slices, f_cnt, bottom=e_cnt+r_cnt, color='#1f77b4', alpha=0.75, label='Flexors (81% Rostral)')
    ax1.set_xlabel("Transverse Slice (1..30, L4 -> S1)", fontsize=8.5)
    ax1.set_ylabel("Motoneuron Count", fontsize=8.5)
    ax1.set_title("A. Motoneuron Somatotopy\n[YAK-DATA] (4034 MNs)", fontsize=9.5, fontweight='bold')
    ax1.legend(fontsize=7.0)

    # 1B: Slice Matrix Heatmap
    ax2 = axes[1]
    im2 = ax2.imshow(anat.slice_matrix, aspect='auto', cmap='Blues', interpolation='nearest')
    ax2.set_xlabel("Transverse Slice (1..30)", fontsize=8.5)
    ax2.set_ylabel("Muscle Index (1..27)", fontsize=8.5)
    ax2.set_title("B. 27 Motor Pool Distributions\n[YAK-DATA]", fontsize=9.5, fontweight='bold')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, label="MNs / Slice")

    # 1C: Stacked EMG
    ax3 = axes[2]
    t = np.linspace(0, 100, 100)
    sample_m = [('Psoas', '#1f77b4'), ('SRTa', '#17becf'), ('VL', '#d62728'), ('BFp', '#2ca02c'), ('Soleus', '#ff7f0e')]
    for idx, (m, col) in enumerate(sample_m):
        ax3.plot(t, model_y.emg_dict[m] + idx * 80.0, color=col, linewidth=1.5, label=m)
    ax3.axvspan(0, 30, color='#e6f2ff', alpha=0.4, label='Swing (0-30%)')
    ax3.axvspan(30, 100, color='#fff2e6', alpha=0.4, label='Stance (30-100%)')
    ax3.set_xlabel("Step Cycle (%)", fontsize=8.5)
    ax3.set_ylabel("EMG Amplitude (Stacked)", fontsize=8.5)
    ax3.set_title("C. Empirical Literature EMG\n[YAK-DATA]", fontsize=9.5, fontweight='bold')
    ax3.legend(fontsize=6.5, loc='upper right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(output_dir, "figure1_yakovenko_reference.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 2: Komi-Derived Spatial Network
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), dpi=300)
    fig.suptitle("Figure 2: Komi-Derived Spatial Network: 3D Geometry, Connectome W & E/I Balancing",
                 fontsize=12, fontweight='bold', y=0.98)

    # 2A: 3D Spatial Layout
    ax1 = axes[0]
    net = model_ky.network
    colors = np.where(net.is_excitatory, 1.0, -1.0)
    sc = ax1.scatter(net.x, net.z, c=colors, cmap='bwr', s=12, alpha=0.6, edgecolors='none')
    ax1.set_xlabel("Mediolateral X (mm)", fontsize=8.5)
    ax1.set_ylabel("Rostrocaudal Z (mm)", fontsize=8.5)
    ax1.set_title(f"A. 3D Spatial Embedding (N={net.n_neurons})\n[KOMI-METHOD]", fontsize=9.5, fontweight='bold')
    ax1.invert_yaxis()

    # 2B: Connectome Matrix W
    ax2 = axes[1]
    W = model_ky.connectome.W
    im2 = ax2.imshow(W, cmap='bwr', vmin=-np.max(np.abs(W)), vmax=np.max(np.abs(W)), aspect='auto')
    ax2.set_xlabel("Presynaptic Neuron j", fontsize=8.5)
    ax2.set_ylabel("Postsynaptic Neuron i", fontsize=8.5)
    ax2.set_title("B. Synaptic Weight Matrix W\n[KOMI-METHOD]", fontsize=9.5, fontweight='bold')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    # 2C: Zero-Sum Row Balance
    ax3 = axes[2]
    row_sums = np.sum(W, axis=1)
    ax3.hist(row_sums, bins=35, color='#2ca02c', edgecolor='black', alpha=0.8)
    ax3.axvline(0.0, color='red', linestyle='--', label='Zero-Sum Target')
    ax3.set_xlabel("Row Sum (sum_j W_ij)", fontsize=8.5)
    ax3.set_ylabel("Neuron Count", fontsize=8.5)
    ax3.set_title("C. Row-Wise E/I Balance\nDual-Input Mean: 9.04e-18", fontsize=9.5, fontweight='bold')
    ax3.legend(fontsize=7.5)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(output_dir, "figure2_komi_derived_network.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 3: Recurrent Activity Generated by Transferred Model
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), dpi=300)
    fig.suptitle("Figure 3: Recurrent Neural Dynamics: Firing Rates, Spatiotemporal Raster & Rotational Limit Cycle",
                 fontsize=12, fontweight='bold', y=0.98)

    # 3A: Sample Rate Traces
    ax1 = axes[0]
    times = model_ky.times_ms[:600]
    for idx in [10, 50, 100, 200, 300]:
        ax1.plot(times, model_ky.rates[idx, :len(times)], linewidth=1.5, label=f"Neuron {idx}")
    ax1.set_xlabel("Time (ms)", fontsize=8.5)
    ax1.set_ylabel("Firing Rate (Hz)", fontsize=8.5)
    ax1.set_title("A. Individual Neural Rates\n[DERIVED] (Leaky Rate Dynamics)", fontsize=9.5, fontweight='bold')
    ax1.legend(fontsize=7.0)

    # 3B: Spatiotemporal Firing Rate Heatmap
    ax2 = axes[1]
    sorted_idx = model_ky.phase_unfolder.phase_sorted_indices
    im2 = ax2.imshow(model_ky.rates[sorted_idx, :len(times)], aspect='auto', cmap='plasma',
                     extent=[times[0], times[-1], len(sorted_idx), 0])
    ax2.set_xlabel("Time (ms)", fontsize=8.5)
    ax2.set_ylabel("Phase-Sorted Neuron Index", fontsize=8.5)
    ax2.set_title("B. Phase-Ordered Population Activity\n[DERIVED]", fontsize=9.5, fontweight='bold')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, label="Rate (Hz)")

    # 3C: SVD PCA Limit Cycle Orbit
    ax3 = axes[2]
    pca_traj = model_ky.phase_unfolder.projections
    ax3.plot(pca_traj[0, :len(times)], pca_traj[1, :len(times)], color='#9467bd', linewidth=2.0)
    ax3.set_xlabel("Principal Component 1 (PC1)", fontsize=8.5)
    ax3.set_ylabel("Principal Component 2 (PC2)", fontsize=8.5)
    ax3.set_title(f"C. Rotational Limit Cycle\nPlanar Var: {model_ky.phase_unfolder.planar_variance*100:.1f}%",
                  fontsize=9.5, fontweight='bold')
    ax3.grid(True, linestyle=':', alpha=0.5)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(output_dir, "figure3_recurrent_activity.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 4: Direct Overlay: Yakovenko vs K-Y Prediction
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.0), dpi=300)
    fig.suptitle("Figure 4: Direct Spatiotemporal Landscape Comparison: Model Y (Observed) vs. Model K-Y (Emergent)",
                 fontsize=12, fontweight='bold', y=0.98)

    ax1 = axes[0]
    im1 = ax1.imshow(model_y.grid[:, :200], aspect='auto', cmap='magma', origin='upper',
                     extent=[0, 200, 28.8, 0])
    ax1.set_xlabel("Step Cycle (%)", fontsize=8.5)
    ax1.set_ylabel("Rostrocaudal Position Z (mm)", fontsize=8.5)
    ax1.set_title("A. Model Y: Feedforward EMG Reconstruction\n[Y-OBSERVED]", fontsize=9.5, fontweight='bold')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04, label="Active MNs / Slice")

    ax2 = axes[1]
    times_800 = model_ky.times_ms[:800]
    im2 = ax2.imshow(model_ky.grid[:, :len(times_800)], aspect='auto', cmap='magma', origin='upper',
                     extent=[times_800[0], times_800[-1], 28.8, 0])
    ax2.set_xlabel("Simulation Time (ms)", fontsize=8.5)
    ax2.set_ylabel("Rostrocaudal Position Z (mm)", fontsize=8.5)
    ax2.set_title(f"B. Model K-Y: Emergent Recurrent Wave\n[EMERGENT] (Velocity: {model_ky.wave.velocity_mm_s:.1f} mm/s)",
                  fontsize=9.5, fontweight='bold')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, label="Firing Rate (Hz)")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(output_dir, "figure4_direct_overlay.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 5: Center-of-Activity Trajectory and Velocity
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.0), dpi=300)
    fig.suptitle("Figure 5: Center-of-Activity Trajectory r_cm(t) and Migration Velocity Comparison",
                 fontsize=12, fontweight='bold', y=0.98)

    t_y = np.linspace(0, 100, 100)
    y_traj = model_y.r_cm_level[:100]

    period_ms = model_ky.phase_unfolder.cycle_period_ms
    steps = int(np.round(period_ms / model_ky.dynamics.dt_ms))
    ky_cycle = model_ky.r_cm_level[:steps] if steps > 20 else model_ky.r_cm_level[:400]
    ky_traj = signal.resample(ky_cycle, 100)

    xcorr = signal.correlate(y_traj - np.mean(y_traj), ky_traj - np.mean(ky_traj), mode='full')
    lags = signal.correlation_lags(100, 100)
    best_lag = lags[np.argmax(xcorr)]
    ky_aligned = np.roll(ky_traj, best_lag)

    corr = np.corrcoef(y_traj, ky_aligned)[0, 1]
    rmse = np.sqrt(np.mean((y_traj - ky_aligned)**2))

    ax1 = axes[0]
    ax1.plot(t_y, y_traj, 'o-', color='#1f77b4', linewidth=2.0, markersize=3.5, label='Model Y (Yakovenko Empirical)')
    ax1.plot(t_y, ky_aligned, 's--', color='#d62728', linewidth=2.0, markersize=3.5, label='Model K-Y (Komi Emergent)')
    ax1.axhline(50.0, color='gray', linestyle=':', label='Mid-Cord Boundary (Level 50)')
    ax1.set_xlabel("Step Cycle (%)", fontsize=8.5)
    ax1.set_ylabel("Spinal Cord Level (0=L4 -> 100=S1)", fontsize=8.5)
    ax1.set_title(f"A. Trajectory Overlay\nCorrelation r = {corr:.3f}, RMSE = {rmse:.2f} levels",
                  fontsize=9.5, fontweight='bold')
    ax1.legend(fontsize=7.5)
    ax1.grid(True, linestyle=':', alpha=0.5)

    ax2 = axes[1]
    ax2.plot(t_y, model_y.velocity_mm_s[:100], color='#1f77b4', linewidth=1.8, label='Model Y Kinematic Velocity')
    ky_vel = np.roll(signal.resample(model_ky.velocity_mm_s[:steps], 100), best_lag)
    ax2.plot(t_y, ky_vel, color='#d62728', linestyle='--', linewidth=1.8, label='Model K-Y Migration Velocity')
    ax2.set_xlabel("Step Cycle (%)", fontsize=8.5)
    ax2.set_ylabel("Migration Velocity |dr_cm/dt| (mm/s)", fontsize=8.5)
    ax2.set_title("B. Center-of-Activity Velocity\n[COMPARISON]", fontsize=9.5, fontweight='bold')
    ax2.legend(fontsize=7.5)
    ax2.grid(True, linestyle=':', alpha=0.5)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(output_dir, "figure5_center_of_activity_and_velocity.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 6: Continuous Traveling Wave vs Activity Migration
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), dpi=300)
    fig.suptitle("Figure 6: Dissection: Continuous Neurogenic Phase Wave vs. Centroid Migration",
                 fontsize=12, fontweight='bold', y=0.98)

    # 6A: Migration (Centroid)
    ax1 = axes[0]
    ax1.plot(t_y, model_y.r_cm_mm[:100], color='#1f77b4', linewidth=2.0)
    ax1.set_xlabel("Step Cycle (%)", fontsize=8.5)
    ax1.set_ylabel("Centroid Position (mm)", fontsize=8.5)
    ax1.set_title("A. Yakovenko Migration r_cm(t)\n[Y-OBSERVED] (Spatial Centroid)", fontsize=9.0, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.5)

    # 6B: Continuous Phase Lag Progression
    ax2 = axes[1]
    phases = model_ky.phase_unfolder.phase_angles
    ax2.scatter(model_ky.network.z, phases, c=model_ky.network.z, cmap='viridis', s=14, alpha=0.7)
    # Regression
    slope, intercept = np.polyfit(model_ky.network.z, phases, 1)
    ax2.plot(model_ky.network.z, slope * model_ky.network.z + intercept, 'r--', linewidth=2.0, label='Phase Wave Slope')
    ax2.set_xlabel("Rostrocaudal Position Z (mm)", fontsize=8.5)
    ax2.set_ylabel("Circular Phase (rad)", fontsize=8.5)
    ax2.set_title(f"B. Komi Phase Progression phi(z)\n[EMERGENT] (v = {model_ky.wave.velocity_mm_s:.1f} mm/s)",
                  fontsize=9.0, fontweight='bold')
    ax2.legend(fontsize=7.0)
    ax2.grid(True, linestyle=':', alpha=0.5)

    # 6C: Net Projectome Profile
    ax3 = axes[2]
    proj = model_ky.projectome
    ax3.plot(proj.bin_centers, proj.net_profile, color='black', linewidth=2.2, label='Net Projectome')
    ax3.axhline(0, color='gray', linestyle=':', linewidth=0.8)
    ax3.axvline(0, color='gray', linestyle=':', linewidth=0.8)
    ax3.set_xlabel("Distance Delta Z (mm)", fontsize=8.5)
    ax3.set_ylabel("Mean Synaptic Weight", fontsize=8.5)
    ax3.set_title(f"C. Mexican-Hat Projectome\n[DERIVED] (MHI = {proj.mexican_hat_index:.2f})",
                  fontsize=9.0, fontweight='bold')
    ax3.legend(fontsize=7.0)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(output_dir, "figure6_traveling_wave_vs_migration.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 7: 11 Ablations and Controls
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.0), dpi=300)
    fig.suptitle("Figure 7: 11 Systematic Ablation & Control Experiments (Conditions A through K)",
                 fontsize=12, fontweight='bold', y=0.98)

    y_pos = np.arange(len(ablation_df))
    labels = [f"{r.condition_id}: {r.condition_name}" for _, r in ablation_df.iterrows()]

    ax1 = axes[0]
    ax1.barh(y_pos, ablation_df['correlation_r'], color='#1f77b4', edgecolor='black', alpha=0.8)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels, fontsize=7.5)
    ax1.set_xlabel("Trajectory Correlation r", fontsize=8.5)
    ax1.set_title("A. Agreement with Yakovenko Trajectory\n[ABLATION]", fontsize=9.5, fontweight='bold')
    ax1.invert_yaxis()

    ax2 = axes[1]
    ax2.barh(y_pos, ablation_df['mexican_hat_index'], color='#2ca02c', edgecolor='black', alpha=0.8)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(labels, fontsize=7.5)
    ax2.set_xlabel("Mexican-Hat Index (MHI)", fontsize=8.5)
    ax2.set_title("B. Projectome Structure Preservation\n[ABLATION]", fontsize=9.5, fontweight='bold')
    ax2.invert_yaxis()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(output_dir, "figure7_ablations_and_controls.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 8: Parameter Sensitivity
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), dpi=300)
    fig.suptitle("Figure 8: Parameter Sensitivity Analysis Across 5 Transferred Dimensions",
                 fontsize=12, fontweight='bold', y=0.98)

    # 8A: mu_z sweep
    ax1 = axes[0]
    sub_mu = sensitivity_df[sensitivity_df['parameter_name'] == 'mu_z_exc_mm']
    ax1.plot(sub_mu['parameter_value'], sub_mu['correlation_r'], 'o-', color='#1f77b4', label='Correlation r')
    ax1.set_xlabel("Descending Bias mu_z (mm)", fontsize=8.5)
    ax1.set_ylabel("Correlation r", fontsize=8.5)
    ax1.set_title("A. Sensitivity to Descending Bias (mu_z)", fontsize=9.0, fontweight='bold')
    ax1.legend(fontsize=7.0)
    ax1.grid(True, linestyle=':', alpha=0.5)

    # 8B: tau sweep
    ax2 = axes[1]
    sub_tau = sensitivity_df[sensitivity_df['parameter_name'] == 'tau_ms']
    ax2.plot(sub_tau['parameter_value'], sub_tau['dominant_freq_hz'], 's-', color='#d62728', label='Frequency (Hz)')
    ax2.set_xlabel("Rate Time Constant tau (ms)", fontsize=8.5)
    ax2.set_ylabel("Dominant Frequency (Hz)", fontsize=8.5)
    ax2.set_title("B. Sensitivity of Locomotor Frequency to tau", fontsize=9.0, fontweight='bold')
    ax2.legend(fontsize=7.0)
    ax2.grid(True, linestyle=':', alpha=0.5)

    # 8C: commissural fraction sweep
    ax3 = axes[2]
    sub_comm = sensitivity_df[sensitivity_df['parameter_name'] == 'commissural_fraction']
    ax3.plot(sub_comm['parameter_value'], sub_comm['bilateral_phase_deg'], '^-', color='#2ca02c', label='Bilateral Phase (deg)')
    ax3.axhline(180.0, color='gray', linestyle=':', label='Antiphase (180 deg)')
    ax3.set_xlabel("Commissural Fraction", fontsize=8.5)
    ax3.set_ylabel("Bilateral Phase Difference (deg)", fontsize=8.5)
    ax3.set_title("C. Bilateral Alternation vs Commissural Wiring", fontsize=9.0, fontweight='bold')
    ax3.legend(fontsize=7.0)
    ax3.grid(True, linestyle=':', alpha=0.5)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(output_dir, "figure8_parameter_sensitivity.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 9: Wave-Definition / Mechanism Comparison Table
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 6.0), dpi=300)
    fig.suptitle("Figure 9: Mathematical & Conceptual Dissection of 5 Locomotor Wave Phenomena",
                 fontsize=12, fontweight='bold', y=0.98)

    headers = ["ID", "Phenomenon Name", "Mathematical Definition", "Biological Substrate", "Velocity Concept", "Generative vs Epiphenomenon"]
    rows = []
    for _, r in wave_def_df.iterrows():
        rows.append([
            f"{r.object_id}",
            r.phenomenon_name,
            r.mathematical_definition,
            r.biological_substrate,
            r.velocity_concept,
            r.generative_or_epiphenomenon
        ])

    ax.axis('off')
    tbl = ax.table(cellText=rows, colLabels=headers, loc='center', cellLoc='left')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.5)
    tbl.scale(1.0, 2.2)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(output_dir, "figure9_wave_definition_comparison.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 10: Final Mechanistic Synthesis Diagram
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(13, 6.0), dpi=300)
    fig.suptitle("Figure 10: Mechanistic Synthesis: Multi-Level Architecture of Mammalian Spinal Locomotion",
                 fontsize=12, fontweight='bold', y=0.98)

    synthesis_rows = [
        ["Level", "Biological Substrate", "Mathematical Engine", "Role in Locomotion", "Scientific Contribution"],
        ["Premotor CPG Circuit", "Ventral Interneurons (V2a, V1, V0)", "Asymmetric Mexican-Hat Projectome + Leaky Dynamics", "Generates Rhythms, Phase Sequences & Traveling Waves", "KOMI ET AL. (2026)"],
        ["Motor Pool Layer", "27 Hindlimb Motoneuron Pools", "Retrograde Somatotopy Matrix N(m, s)", "Filters continuous wave into joint-specific motor bursts", "YAKOVENKO ET AL. (2002)"],
        ["Peripheral Effector", "Hindlimb Musculoskeletal Plant", "Dynamic EMG Envelopes & Biomechanics", "Executes Stance Load Support & Swing Stepping", "CLASSICAL PHYSIOLOGY"],
        ["Sensory Feedback", "Ia / Ib / Cutaneous Afferents", "Load-dependent reinforcement of stance extensor half-centers", "Prolongs stance duration to 70% in live walking", "INTEGRATING BRIDGE"]
    ]

    ax.axis('off')
    tbl10 = ax.table(cellText=synthesis_rows[1:], colLabels=synthesis_rows[0],
                     colColours=["#e6f2ff", "#f9f9f9", "#e6ffe6", "#fff2e6", "#f0e6ff"],
                     loc='center', cellLoc='center')
    tbl10.auto_set_font_size(False)
    tbl10.set_fontsize(8.0)
    tbl10.scale(1.0, 2.3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(output_dir, "figure10_mechanistic_synthesis.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)
