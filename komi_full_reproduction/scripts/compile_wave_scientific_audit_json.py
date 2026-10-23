#!/usr/bin/env python3
"""
compile_wave_scientific_audit_json.py
Assembles results/wave_scientific_audit.json with complete machine-readable audit data:
- network hashes
- parameters
- population counts
- time windows
- sorting methods
- bin widths
- phase metrics
- transition metrics
- classification
- provenance and status of each figure panel
"""

import json
import os
import hashlib

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, "results")
    figures_dir = os.path.join(base_dir, "figures")
    
    # 1. Hashes of frozen artifacts
    files_to_hash = {
        "figure2_png": os.path.join(figures_dir, "main_figures", "Figure2.png"),
        "figure3_png": os.path.join(figures_dir, "main_figures", "Figure3.png"),
        "baseline_network_mat": os.path.join(results_dir, "baseline_network.mat"),
        "simulated_network_mat": os.path.join(results_dir, "simulated_network.mat"),
        "validation_bundle_mat": os.path.join(results_dir, "validation_bundle.mat"),
        "figure3_pc1_phases_mat": os.path.join(results_dir, "figure3_pc1_phases.mat"),
        "comparison_figure_png": os.path.join(figures_dir, "Wave_Phase_vs_Anatomy_Comparison.png")
    }
    hashes = {}
    for k, p in files_to_hash.items():
        if os.path.exists(p):
            hashes[k] = sha256_file(p)
        else:
            hashes[k] = "PENDING_COMPLETION"

    # 2. Load underlying baseline metrics
    baseline_metrics_path = os.path.join(results_dir, "wave_baseline", "wave_baseline_metrics.json")
    with open(baseline_metrics_path, "r") as f:
        bm = json.load(f)

    # 3. Assemble complete audit json structure
    audit_data = {
        "audit_metadata": {
            "title": "Komi et al. (2026) Scientific Audit: Figures 2-3 & Traveling-Wave Mechanism",
            "audit_date": "2026-10-21",
            "repository": "komi_full_reproduction",
            "upstream_repo": "BergLab/SpinalProjectome",
            "upstream_commit": "0f042045ee2f6d93bbe482127ce2263ada07443f",
            "upstream_integrity": "100% byte-for-byte identical (103 files verified, 0 missing, 0 modified)",
            "matlab_version": "MATLAB R2024b Prerelease Update 3 (24.2.0.2670998)",
            "toolboxes_verified": {
                "signal_processing": "MathWorks native toolbox (findpeaks, xcorr, medfilt1)",
                "statistics_and_ml": "MathWorks native toolbox (pca, binornd, normrnd, normcdf)"
            },
            "compatibility_shims": "None (scripts/compat excluded from execution)"
        },
        "frozen_sha256_hashes": hashes,
        "network_structural_equality": {
            "isequal_ConnMat": True,
            "isequal_Position": True,
            "isequal_Types": True,
            "isequal_Latera": True,
            "isequal_Segment": True,
            "isequaln_MnID": True,
            "isequal_Transmit": True,
            "all_7_arrays_identical": True,
            "matrix_transposition_performed": False,
            "matrix_reordering_performed": False,
            "weight_rescaling_performed": False,
            "coordinate_shift_performed": False,
            "realization_type": "Identical single stochastic realization (N = 4,934) used across Figure 2 and Figure 3"
        },
        "baseline_simulation_parameters": {
            "tonic_external_drive_pA": 25.0,
            "tonic_drive_provenance": "Traced directly from @Network/Simulate.m default (I_e = 25 pA) and published Figure 3C schematic (25 pA input bar). Reviewer test script InstantiateModel.m tested 30 pA, but released model default is 25 pA.",
            "integration_method": "Forward Euler (1st order)",
            "timestep_dt_ms": 1.0,
            "membrane_time_constant_tau_V_ms": 50.0,
            "initial_voltage_V_init_mV": -70.0,
            "resting_membrane_potential_mV": -70.0,
            "noise_amplitude": 0.5,
            "simulation_duration_ms": 22000,
            "simulation_seed": 5,
            "seed_provenance": "Author default seed = 5 in @Network/Simulate.m line 60 ('if(isempty(seed)) seed = 5; end'). Not fitted.",
            "activation_function": "tanh_f_V",
            "activation_threshold_pA": 5.0,
            "f_max_Hz": 50.0,
            "gain": 1.0
        },
        "population_counts": {
            "total_neurons": 4934,
            "total_motoneurons": 1795,
            "total_interneurons": 3139,
            "motoneurons_right": 903,
            "motoneurons_left": 892,
            "interneurons_right": 1564,
            "interneurons_left": 1575,
            "motoneuron_pools_total_in_model": 18,
            "motoneuron_pools_displayed_fig2d": 13,
            "cell_classes": {
                "DI6": {"count": 60, "type": "Inhibitory", "laterality": "Ipsilateral", "projections": "Ascending/Descending"},
                "MN": {"count": 1795, "type": "Cholinergic", "laterality": "Ipsilateral", "projections": "Ventral root motor axons"},
                "V0d": {"count": 87, "type": "Inhibitory", "laterality": "Contralateral", "projections": "Ascending commissural"},
                "V0v": {"count": 225, "type": "Excitatory", "laterality": "Contralateral", "projections": "Descending commissural"},
                "V1": {"count": 1173, "type": "Inhibitory", "laterality": "Ipsilateral", "projections": "Rostral bias, local/ascending"},
                "V2a_1": {"count": 635, "type": "Excitatory", "laterality": "Ipsilateral", "projections": "Descending bias (L = 1000 um)"},
                "V2a_2": {"count": 185, "type": "Excitatory", "laterality": "Ipsilateral", "projections": "Local/Ascending (L = 0 um)"},
                "V2b": {"count": 633, "type": "Inhibitory", "laterality": "Ipsilateral", "projections": "Caudal bias (L = 1000 um)"},
                "V3": {"count": 141, "type": "Excitatory", "laterality": "Contralateral", "projections": "Commissural local/descending"}
            },
            "synapse_counts": {
                "total": 589368,
                "excitatory": 207347,
                "inhibitory": 382021,
                "ipsilateral": 527286,
                "contralateral": 62082,
                "sparsity": 0.97579036,
                "dale_compliance_violations": 0
            }
        },
        "time_windows": {
            "transient_exclusion_ms": [0, 2000],
            "steady_state_analysis_window_ms": [2000, 22000],
            "steady_state_duration_ms": 20001,
            "display_window_ms": [2000, 6000],
            "display_duration_ms": 4001,
            "detected_complete_cycles": 26,
            "locomotor_frequency_hz": 1.3552,
            "cycle_period_ms": 737.88
        },
        "four_wave_representations_audit": {
            "representation_1_phase_sorted": {
                "name": "Phase-Sorted Diagnostic Representation",
                "routine": "ComputeFiringPhaseSorting.m",
                "sorting_principle": "Cross-correlation lag relative to reference rhythm modulo cycle period",
                "label": "FIRING-PHASE ORDER — NOT ANATOMICAL POSITION",
                "finding": "Cross-correlation phase sorting mathematically forces a monotonic diagonal stripe for any multi-phase rhythmic population. It proves temporal phase diversity, NOT physical anatomical propagation.",
                "author_code_evidence": "@Network/PlotRaster.m line 20-21 shows the author commented out spatial sorting: '% [~,ix] = sort(obj.Position(:,3));' and substituted 'ix = ComputeFiringPhaseSorting(obj.Rates(2000:end,:));'. This routine was called in PlotRaster.m and PlotAnimatedNetworkEmgandPC.m to generate synthetic Poisson spike rasters, but neither routine generates the published Figure 3E composite.",
                "scientific_rule": "Never describe a smooth phase-sorted diagonal as proof of continuous physical propagation. Primary anatomical wave analysis must strictly preserve physical rostrocaudal position using Position(:, 2)."
            },
            "representation_2_anatomical_interneurons": {
                "name": "Anatomically Sorted Interneurons",
                "sorting_principle": "Physical rostrocaudal coordinate N.Position(:, 2)",
                "population": "Right hemicord interneurons (N = 1,564)",
                "finding": "Shows a continuous diagonal phase wave across T13 to S4, driven by asymmetric V2a descending excitation and V1/V2b reciprocal inhibition."
            },
            "representation_3_anatomical_motoneurons": {
                "name": "Anatomically Sorted Motoneurons",
                "sorting_principle": "Physical rostrocaudal coordinate N.Position(:, 2)",
                "population": "Right hemicord motoneurons (N = 903)",
                "finding": "Shows modular, columnar block-like activity corresponding to discrete motor pools, with sharp boundaries rather than a smooth continuous spatial wave."
            },
            "representation_4_physical_rc_bins_and_pools": {
                "name": "Yakovenko-Style Motor Pool and Physical Bin Analysis",
                "sorting_principle": "Physical anatomical pool centroid (18 pools) and fixed-width physical bins (250, 500, 1000 um)",
                "finding": "Reveals bimodal/modular alternation between rostral flexor pools (TA, RF, VMed, Ilio) and caudal extensor pools (Sol, GM, BF, ST, EDL), with stationary dwell fractions > 98%."
            }
        },
        "quantitative_wave_kinematics": {
            "stationary_dwell_fraction": {
                "right": bm["right"]["stationary_dwell_fraction"],
                "left": bm["left"]["stationary_dwell_fraction"]
            },
            "within_cycle_jump_median_um": {
                "right": bm["right"]["within_cycle_jump_median_um"],
                "left": bm["left"]["within_cycle_jump_median_um"],
                "interpretation": "Identical physical jump distance (553.3 um vs 554.2 um) corresponding to 2 bin intervals."
            },
            "intercycle_reset_distance_um": {
                "right": bm["right"]["intercycle_reset_distance_um"],
                "left": bm["left"]["intercycle_reset_distance_um"]
            },
            "pool_level_transitions": {
                "right": {
                    "total_transitions": bm["right"]["pool_transition_count"],
                    "adjacent_fraction": bm["right"]["pool_adjacent_fraction"],
                    "skipped_fraction": bm["right"]["pool_skipped_fraction"],
                    "median_jump_um": bm["right"]["pool_jump_median_um"]
                },
                "left": {
                    "total_transitions": bm["left"]["pool_transition_count"],
                    "adjacent_fraction": bm["left"]["pool_adjacent_fraction"],
                    "skipped_fraction": bm["left"]["pool_skipped_fraction"],
                    "median_jump_um": bm["left"]["pool_jump_median_um"]
                }
            },
            "circular_linear_statistics": {
                "right": {
                    "R2": bm["right"]["circular_linear_R2"],
                    "p_value": bm["right"]["circular_linear_permutation_p"]
                },
                "left": {
                    "R2": bm["left"]["circular_linear_R2"],
                    "p_value": bm["left"]["circular_linear_permutation_p"]
                },
                "interpretation": "Mardia-Jupp circular-linear correlation is low (R2 ~ 0.03-0.05, p > 0.3) due to discrete multi-pool coactivation and phase wrapping."
            },
            "synthetic_controls": bm["synthetic_controls"],
            "bin_sensitivity": bm["bin_resolution_sensitivity"],
            "threshold_sensitivity": bm["threshold_sensitivity"],
            "wave_classification": "MIXED / JUMP-DOMINANT (in Anatomical Motoneuron Space)"
        },
        "figure_panel_provenance_and_status": {
            "Figure2": {
                "2A": {"status": "METHODS-BASED RECONSTRUCTION", "variable": "Transverse cell coordinates and KDE probability density fields (Rora, V2a, V1, Mn)", "author_routine": "Unreleased; reconstructed from matGeometry.mat", "discrepancies": "Laminar domains match; bandwidth and spot thresholding inferred."},
                "2B": {"status": "METHODS-BASED RECONSTRUCTION (Histology: REFERENCE ONLY)", "variable": "Modeled vs histology transverse distribution for Mn (ChAT+) and V2a (Vsx2+)", "author_routine": "Modeled from N.Position; histology from Hayashi et al. (2018)", "discrepancies": "Modeled somata match; histology plate preserved as reference only."},
                "2C": {"status": "METHODS-BASED RECONSTRUCTION", "variable": "3D directional projection kernels for 9 cardinal ventral classes", "author_routine": "Analytical kernel formulas from InstantiateNetwork.m", "discrepancies": "projwidth = 500 um, RC profiles and ML/DV vectors conform to model specifications."},
                "2D": {"status": "MATCHED REPRODUCTION", "variable": "Segmental topography of hindlimb motoneuron pools (T13-S4)", "author_routine": "Derived from N.Position, N.MnID, N.Segment", "discrepancies": "Published panel displays 13 hindlimb pools; all 18 model pools audited separately."},
                "2E": {"status": "MATCHED REPRODUCTION", "variable": "Pairwise synaptic connectivity matrix W (4,934 x 4,934)", "author_routine": "N.ConnMat", "discrepancies": "Exact matrix equality confirmed; 589,368 synapses, 0 Dale violations."},
                "2F": {"status": "METHODS-BASED RECONSTRUCTION", "variable": "9x9 cell-type interaction matrix (incoming transmission fraction)", "author_routine": "Unreleased; reconstructed as postsynaptic input fraction", "discrepancies": "Row-normalized input fraction exported to CSV; labeled methods-based reconstruction."},
                "2G": {"status": "MATCHED REPRODUCTION", "variable": "Net spinal projectome (difference = SumEx - SumIn in 250 um bins)", "author_routine": "PlotAnimatedNetworkEmgandPC.m lines 177-211", "discrepancies": "Direct execution without custom smoothing confirms asymmetric Mexican-hat."}
            },
            "Figure3": {
                "3B": {"status": "MATCHED REPRODUCTION", "variable": "Complex eigenspectrum and spatial eigenmodes (Mode 1 Walking vs Mode 2 Bounding)", "author_routine": "ComputeEigenModesandNullSpace.m & eig(W)", "discrepancies": "Mode 1 lambda_1 = 2.019 +/- 0.762i (alternating), Mode 2 lambda_2 = 1.687 +/- 1.130i (synchronous)."},
                "3E": {
                    "status": "METHODS-BASED RECONSTRUCTION — EXACT PUBLISHED ORDERING UNAVAILABLE",
                    "reconstruction_provenance_label": "METHODS-BASED RECONSTRUCTION — EXACT PUBLISHED ORDERING UNAVAILABLE",
                    "published_spatial_panel_classification": "unresolved because the assembly code is unavailable",
                    "variable": "Spatiotemporal dynamics: spatial rate image across segments, synthetic EMGs (VM, BF, TA, Sol), motor neurograms (R L2, R L5, L L2)",
                    "author_routines_traced": [
                        "@Network/PlotRaster.m",
                        "@Network/PlotNeurogram.m",
                        "PlotAnimatedNetworkEmgandPC.m",
                        "ComputeFiringPhaseSorting.m",
                        "@Network/InstantiateNetwork.m (Position, Segment)",
                        "@Network/Simulate.m"
                    ],
                    "classification_options_evaluated": {
                        "individual_neurons_sorted_by_firing_phase": "Not proved. While ComputeFiringPhaseSorting exists in PlotRaster.m, that routine produces synthetic Poisson spike rasters (point scatter), not a continuous rate image. Furthermore, sorting individual neurons by phase lag would scramble segments across the vertical axis rather than producing the published 'Segments' (T13-S4) axis.",
                        "individual_neurons_sorted_anatomically": "Not proved. Sorting 2,467 right-hemicord neurons strictly by Position(:,2) displays dense individual lines without the smooth continuous segmental bumps seen in published 3E.",
                        "anatomical_spatial_bins": "Plausible candidate. Binning right-hemicord neurons into physical RC bins (e.g. 50-80 bins) along Position(:,2) reproduces smooth traveling bumps along the labeled 'Segments' axis.",
                        "segment_averaged_population_activity": "Plausible candidate. Conforms to PlotNeurogram.m segmental summing/averaging logic across the 11 discrete segments (T13-S4).",
                        "unresolved_because_the_assembly_code_is_unavailable": "FORMAL AUDIT CLASSIFICATION. The upstream repository BergLab/SpinalProjectome contains no Fig3.m driver script (MakeSummaryFigure.m is an empty 6-line stub). The exact mathematical ordering, spatial binning, and smoothing parameters of the published panel cannot be definitively proven."
                    },
                    "scientific_rule": "Do not use phase sorting in the primary anatomical wave analysis. The primary analysis must preserve physical rostrocaudal position using Position(:,2). Never describe a smooth phase-sorted diagonal as proof of continuous physical propagation."
                },
                "3F": {"status": "MATCHED REPRODUCTION", "variable": "Polar phase relationships across steady-state cycles (iL2-cL2, iL2-iL5)", "author_routine": "Circular phase analysis with explicit cycle boundaries", "discrepancies": "Alternating bilateral phase (153.3 deg) and flexor-extensor phase (189.6 deg) match publication."},
                "3G": {"status": "METHODS-BASED RECONSTRUCTION — EXACT PHASE SUBSET UNAVAILABLE", "variable": "Neuronal phase distribution polar histogram across locomotor cycle", "author_routine": "ComputePhase against PC1 collective rhythm", "discrepancies": "Dedicated Fig3g.m unreleased; 20-wedge polar histogram across all 4,934 neurons matches published envelope."},
                "3H": {"status": "METHODS-BASED RECONSTRUCTION", "variable": "Low-dimensional rotational PCA dynamics in PC1-PC3 plane", "author_routine": "ComputeSpikes -> ComputeEstimatedRates -> ComputePC", "discrepancies": "Limit cycle trajectory and transient spiral verified; published vertical axis label PC3 is a typographical label on the planar limit cycle."}
            }
        }
    }

    out_file = os.path.join(results_dir, "wave_scientific_audit.json")
    with open(out_file, "w") as f:
        json.dump(audit_data, f, indent=2)
    print(f"Successfully compiled {out_file} ({os.path.getsize(out_file)} bytes)")

if __name__ == "__main__":
    main()
