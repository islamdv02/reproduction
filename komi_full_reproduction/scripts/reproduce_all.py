#!/usr/bin/env python3
"""
Master Entry Point: reproduce_all.py
Komi et al. (2026) Strict Baseline Reproduction Pipeline
BergLab/SpinalProjectome (commit 0f042045ee2f6d93bbe482127ce2263ada07443f)

Sequentially reproduces available computational figures from released routines,
compiles canonical metrics, and generates the authoritative comparison PDF
(Komi_reproduction_comparison.pdf).
"""

import os
import sys
import argparse
import subprocess
import time


def run_cmd(cmd_list, desc, cwd):
    print(f"\n{'='*70}")
    print(f"[*] RUNNING: {desc}")
    print(f"[*] Command: {' '.join(cmd_list)}")
    print(f"{'='*70}")
    t0 = time.time()
    res = subprocess.run(cmd_list, cwd=cwd, shell=False)
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"[!] ERROR in {desc} (Exit code: {res.returncode}, Time: {elapsed:.1f}s)")
        return False
    print(f"[+] SUCCESS: {desc} ({elapsed:.1f}s)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Komi et al. (2026) Strict Baseline Pipeline")
    parser.add_argument("--full-simulation", action="store_true",
                        help="Re-run raw network construction and 4-second dynamics simulation (takes ~15-20 min)")
    parser.add_argument("--step", type=str, default="all",
                        choices=["all", "fig1", "fig2", "fig3", "fig4", "fig5", "supp", "metrics", "pdf"],
                        help="Run a specific figure step or 'all'")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scripts_dir = os.path.join(repo_root, "scripts")
    results_dir = os.path.join(repo_root, "results")

    MATLAB_BIN = r"C:\Program Files\MATLAB\R2024b\bin\matlab.exe"
    if not os.path.exists(MATLAB_BIN):
        # Fallback to bare matlab only if R2024b not at standard location
        MATLAB_BIN = "matlab"

    # Step 1: Raw simulation (if requested or if raw data missing)
    baseline_net = os.path.join(results_dir, "baseline_network.mat")
    simulated_net = os.path.join(results_dir, "simulated_network.mat")

    if args.full_simulation or not (os.path.exists(baseline_net) and os.path.exists(simulated_net)):
        print("\n[>>>] STEP 1 & 2: Network Construction & Dynamics Simulation")
        if not run_cmd([MATLAB_BIN, "-batch", "run('scripts/run_network_construction.m')"],
                       "Network Construction (4,934 neurons)", repo_root):
            sys.exit(1)
        if not run_cmd([MATLAB_BIN, "-batch", "run('scripts/run_baseline_simulation.m')"],
                       "Baseline Dynamics Simulation (4 seconds, dt=0.2ms)", repo_root):
            sys.exit(1)
    else:
        print("\n[i] Using existing raw simulation data: baseline_network.mat and simulated_network.mat")

    # Reproduction steps (strictly available released figures)
    steps_to_run = []
    if args.step == "all":
        steps_to_run = ["fig1", "fig2", "fig3", "fig4", "fig5", "pools", "bundle", "metrics", "panel_val", "pdf"]
    else:
        steps_to_run = [args.step]

    success = True
    for s in steps_to_run:
        if s == "fig1":
            success = run_cmd([sys.executable, os.path.join(scripts_dir, "build_figure1_composite.py")],
                              "Figure 1: Published Reference Composite Assembly", repo_root)
        elif s == "fig2":
            success = run_cmd([MATLAB_BIN, "-batch", "run('scripts/run_figure2_reproduction.m')"],
                              "Figure 2: 3D Model Architecture & Transverse Anatomy", repo_root)
        elif s == "fig3":
            success = run_cmd([MATLAB_BIN, "-batch", "run('scripts/run_figure3_reproduction.m')"],
                              "Figure 3: Emergent Dynamics, Heatmap, EMGs, Neurograms, Polar Phase, PCA", repo_root)
        elif s == "fig4":
            success = run_cmd([MATLAB_BIN, "-batch", "run('scripts/run_figure4_reproduction.m')"],
                              "Figure 4: Descending Gain Modulation & Multi-Gait Transitions", repo_root)
        elif s == "fig5":
            success = run_cmd([MATLAB_BIN, "-batch", "run('scripts/run_figure5_reproduction.m')"],
                              "Figure 5: Genetic Manipulation (V1 & V0 Silencing/Ablation)", repo_root)
        elif s == "supp":
            success = run_cmd([MATLAB_BIN, "-batch", "run('scripts/run_supplementary_figures.m')"],
                              "Supplementary Figures (S4, S6, S7, S8, S11, S12)", repo_root)
        elif s == "pools":
            success = run_cmd([MATLAB_BIN, "-batch", "run('scripts/export_motoneuron_pools.m')"],
                              "Motoneuron Pools Machine-Readable Table Export", repo_root)
        elif s == "bundle":
            success = run_cmd([MATLAB_BIN, "-batch", "run('scripts/export_validation_bundle.m')"],
                              "Validation Bundle Export (results/validation_bundle.mat)", repo_root)
        elif s == "metrics":
            success = run_cmd([sys.executable, os.path.join(scripts_dir, "compile_central_metrics.py")],
                              "Central Metrics Compiler (reproduction_metrics.json)", repo_root)
        elif s == "panel_val":
            success = run_cmd([sys.executable, os.path.join(scripts_dir, "generate_panel_validation.py")],
                              "Panel-by-Panel Validation Table Generator (panel_validation.json & PANEL_VALIDATION.md)", repo_root)
        elif s == "pdf":
            success = run_cmd([sys.executable, os.path.join(scripts_dir, "build_comparison_pdf.py")],
                              "Comparison PDF Generator (Komi_reproduction_comparison.pdf)", repo_root)

        if not success:
            print(f"\n[!] Pipeline halted at step: {s}")
            sys.exit(1)

    print(f"\n{'='*70}")
    print("[+] STRICT BASELINE PIPELINE FINISHED SUCCESSFULLY.")
    print(f"[+] Authoritative PDF: {os.path.join(repo_root, 'Komi_reproduction_comparison.pdf')}")
    print(f"[+] Central Metrics:    {os.path.join(results_dir, 'reproduction_metrics.json')}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
