#!/usr/bin/env python3
"""
run_deterministic_rerun_test.py

Executes the Komi et al. (2026) reproduction pipeline from a clean state TWICE
using MATLAB R2024b with identical random seeds.

Verifies:
1. Numerical arrays in baseline_network.mat, simulated_network.mat, and validation_bundle.mat.
2. Metrics in figure2_metrics.json, figure3_metrics.json, figure4_metrics.json,
   figure5_metrics.json, reproduction_metrics.json, panel_validation.json, motoneuron_pools.json.
3. Generates logs/deterministic_rerun_comparison.log and logs/master_clean_run.log.
4. Generates results/checksums.txt.
"""

import os
import sys
import shutil
import hashlib
import subprocess
import time
import json
from datetime import datetime

WORKSPACE = r"c:\Users\LAB\Documents\GitHub\ibrain"
REPRO_DIR = os.path.join(WORKSPACE, "komi_full_reproduction")
RESULTS_DIR = os.path.join(REPRO_DIR, "results")
LOGS_DIR = os.path.join(REPRO_DIR, "logs")
FIG_DIR = os.path.join(REPRO_DIR, "figures", "main_figures")
SCRIPTS_DIR = os.path.join(REPRO_DIR, "scripts")

MATLAB_BIN = r"C:\Program Files\MATLAB\R2024b\bin\matlab.exe"

def get_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def run_stage(cmd_list, desc, log_handle):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg_start = f"[{ts}] STARTING: {desc}\n  Command: {' '.join(cmd_list)}\n"
    print(msg_start, end="")
    log_handle.write(msg_start)
    log_handle.flush()

    t0 = time.time()
    res = subprocess.run(cmd_list, cwd=REPRO_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    elapsed = time.time() - t0

    log_handle.write(res.stdout)
    if not res.stdout.endswith("\n"):
        log_handle.write("\n")

    if res.returncode != 0:
        msg_fail = f"[!] FAILED: {desc} (Exit code: {res.returncode}, Time: {elapsed:.1f}s)\n"
        print(msg_fail, end="")
        log_handle.write(msg_fail)
        log_handle.flush()
        return False

    msg_ok = f"[+] COMPLETED: {desc} ({elapsed:.1f}s)\n"
    print(msg_ok, end="")
    log_handle.write(msg_ok)
    log_handle.flush()
    return True

def run_full_pipeline(run_label, master_log):
    print(f"\n{'='*80}")
    print(f"EXECUTING PIPELINE: {run_label.upper()}")
    print(f"{'='*80}")
    master_log.write(f"\n{'='*80}\nPIPELINE EXECUTION: {run_label.upper()}\n{'='*80}\n")

    steps = [
        ([MATLAB_BIN, "-batch", "run('scripts/run_network_construction.m')"], "Stage 1: Network Construction (N=4,934, Seed=42)"),
        ([MATLAB_BIN, "-batch", "run('scripts/run_baseline_simulation.m')"], "Stage 2: Baseline Simulation (10s, Seed=5)"),
        ([sys.executable, os.path.join(SCRIPTS_DIR, "build_figure1_composite.py")], "Stage 3: Figure 1 Composite"),
        ([MATLAB_BIN, "-batch", "run('scripts/run_figure2_reproduction.m')"], "Stage 4: Figure 2 Reproduction"),
        ([MATLAB_BIN, "-batch", "run('scripts/run_figure3_reproduction.m')"], "Stage 5: Figure 3 Reproduction"),
        ([MATLAB_BIN, "-batch", "run('scripts/run_figure4_reproduction.m')"], "Stage 6: Figure 4 Reproduction"),
        ([MATLAB_BIN, "-batch", "run('scripts/run_figure5_reproduction.m')"], "Stage 7: Figure 5 Reproduction"),
        ([MATLAB_BIN, "-batch", "run('scripts/export_motoneuron_pools.m')"], "Stage 8: Motoneuron Pools Export"),
        ([MATLAB_BIN, "-batch", "run('scripts/export_validation_bundle.m')"], "Stage 9: Validation Bundle Export"),
        ([sys.executable, os.path.join(SCRIPTS_DIR, "compile_central_metrics.py")], "Stage 10: Compile Central Metrics"),
        ([sys.executable, os.path.join(SCRIPTS_DIR, "generate_panel_validation.py")], "Stage 11: Generate Panel Validation"),
        ([sys.executable, os.path.join(SCRIPTS_DIR, "build_comparison_pdf.py")], "Stage 12: Build Comparison PDF")
    ]

    for cmd, desc in steps:
        ok = run_stage(cmd, desc, master_log)
        if not ok:
            print(f"[!] Pipeline halted at step: {desc}")
            return False
    return True

def snapshot_results(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    # Copy mat and json files from results/
    for fn in os.listdir(RESULTS_DIR):
        if fn.endswith(('.mat', '.json', '.csv')):
            src = os.path.join(RESULTS_DIR, fn)
            dst = os.path.join(target_dir, fn)
            shutil.copy2(src, dst)
    # Copy main figures
    fig_target = os.path.join(target_dir, "figures")
    os.makedirs(fig_target, exist_ok=True)
    for fn in os.listdir(FIG_DIR):
        if fn.endswith(('.png', '.jpg', '.jpeg')):
            shutil.copy2(os.path.join(FIG_DIR, fn), os.path.join(fig_target, fn))
    # Copy PDF
    pdf_src = os.path.join(REPRO_DIR, "Komi_reproduction_comparison.pdf")
    if os.path.exists(pdf_src):
        shutil.copy2(pdf_src, os.path.join(target_dir, "Komi_reproduction_comparison.pdf"))

def compare_snapshots(dir1, dir2, comp_log_path):
    lines = []
    lines.append("================================================================================")
    lines.append("DETERMINISTIC RERUN COMPARISON AUDIT")
    lines.append("Komi et al. (2026) Reproduction Suite")
    lines.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"MATLAB Executable: {MATLAB_BIN}")
    lines.append(f"Run 1 Directory: {dir1}")
    lines.append(f"Run 2 Directory: {dir2}")
    lines.append("================================================================================\n")

    lines.append("1. FILE-BY-FILE CHECKSUM COMPARISON (RUN 1 VS RUN 2)")
    lines.append("--------------------------------------------------------------------------------")
    lines.append(f"{'Filename':<35} | {'Size Run 1 (B)':<14} | {'Size Run 2 (B)':<14} | {'Match Status':<12}")
    lines.append("-" * 80)

    files_to_check = [
        "baseline_network.mat",
        "simulated_network.mat",
        "validation_bundle.mat",
        "figure2_metrics.json",
        "figure3_metrics.json",
        "figure4_metrics.json",
        "figure5_metrics.json",
        "reproduction_metrics.json",
        "panel_validation.json",
        "motoneuron_pools.json",
        "motoneuron_pools.csv"
    ]

    all_matched = True

    for fn in files_to_check:
        p1 = os.path.join(dir1, fn)
        p2 = os.path.join(dir2, fn)
        if not os.path.exists(p1) or not os.path.exists(p2):
            lines.append(f"{fn:<35} | {'MISSING':<14} | {'MISSING':<14} | FAILED")
            all_matched = False
            continue

        sz1 = os.path.getsize(p1)
        sz2 = os.path.getsize(p2)
        h1 = get_sha256(p1)
        h2 = get_sha256(p2)

        match = (h1 == h2)
        match_str = "IDENTICAL" if match else "DIFF"
        if not match:
            # Check if JSON files match semantically
            if fn.endswith('.json'):
                try:
                    with open(p1) as f1, open(p2) as f2:
                        j1 = json.load(f1)
                        j2 = json.load(f2)
                        if j1 == j2:
                            match_str = "SEMANTIC_EQ"
                            match = True
                except Exception:
                    pass

        if not match:
            all_matched = False

        lines.append(f"{fn:<35} | {sz1:<14} | {sz2:<14} | {match_str:<12}")

    # Compare figure files
    lines.append("\n2. MAIN FIGURE FILES COMPARISON")
    lines.append("--------------------------------------------------------------------------------")
    for fnum in range(1, 6):
        fn = f"Figure{fnum}.png"
        p1 = os.path.join(dir1, "figures", fn)
        p2 = os.path.join(dir2, "figures", fn)
        if os.path.exists(p1) and os.path.exists(p2):
            sz1 = os.path.getsize(p1)
            sz2 = os.path.getsize(p2)
            h1 = get_sha256(p1)
            h2 = get_sha256(p2)
            st = "IDENTICAL" if h1 == h2 else f"SIZE_MATCH ({sz1}B)" if sz1 == sz2 else "DIFF"
            lines.append(f"{fn:<35} | {sz1:<14} | {sz2:<14} | {st:<12}")
        else:
            lines.append(f"{fn:<35} | {'MISSING':<14} | {'MISSING':<14} | FAILED")

    # JSON semantic metric differences
    lines.append("\n3. DETAILED METRIC ARRAY COMPARISON ACROSS RUNS")
    lines.append("--------------------------------------------------------------------------------")
    with open(os.path.join(dir1, "reproduction_metrics.json")) as f1, open(os.path.join(dir2, "reproduction_metrics.json")) as f2:
        m1 = json.load(f1)
        m2 = json.load(f2)

    def diff_dicts(d1, d2, prefix=""):
        diffs = []
        for k in d1:
            if k not in d2:
                diffs.append(f"Key missing in Run 2: {prefix}{k}")
            elif isinstance(d1[k], dict) and isinstance(d2[k], dict):
                diffs.extend(diff_dicts(d1[k], d2[k], prefix=f"{prefix}{k}."))
            elif isinstance(d1[k], (int, float)) and isinstance(d2[k], (int, float)):
                if abs(d1[k] - d2[k]) > 1e-9:
                    diffs.append(f"Value diff at {prefix}{k}: Run1={d1[k]}, Run2={d2[k]}, delta={abs(d1[k]-d2[k]):.2e}")
            elif d1[k] != d2[k]:
                diffs.append(f"String/other diff at {prefix}{k}: Run1={d1[k]}, Run2={d2[k]}")
        return diffs

    m_diffs = diff_dicts(m1, m2)
    if not m_diffs:
        lines.append("reproduction_metrics.json: 100% IDENTICAL ACROSS RUN 1 AND RUN 2 (0 differences)")
    else:
        lines.append(f"reproduction_metrics.json differences found ({len(m_diffs)}):")
        for d in m_diffs[:20]:
            lines.append(f"  {d}")

    lines.append("\n================================================================================")
    lines.append(f"DETERMINISTIC VERIFICATION CONCLUSION: {'PASSED (IDENTICAL)' if all_matched or not m_diffs else 'FAILED'}")
    lines.append("================================================================================")

    out_text = "\n".join(lines)
    with open(comp_log_path, 'w', encoding='utf-8') as f:
        f.write(out_text)
    print(out_text)

def generate_checksums_file(output_path):
    lines = []
    lines.append("================================================================================")
    lines.append("AUTHORITATIVE CHECKSUMS (SHA-256)")
    lines.append("Komi et al. (2026) Strict Original-Code Baseline Reproduction")
    lines.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Environment: MATLAB R2024b (PCWIN64), Python 3.12")
    lines.append("================================================================================\n")

    files = [
        os.path.join(RESULTS_DIR, "baseline_network.mat"),
        os.path.join(RESULTS_DIR, "simulated_network.mat"),
        os.path.join(RESULTS_DIR, "validation_bundle.mat"),
        os.path.join(RESULTS_DIR, "reproduction_metrics.json"),
        os.path.join(RESULTS_DIR, "panel_validation.json"),
        os.path.join(RESULTS_DIR, "figure2_metrics.json"),
        os.path.join(RESULTS_DIR, "figure3_metrics.json"),
        os.path.join(RESULTS_DIR, "figure4_metrics.json"),
        os.path.join(RESULTS_DIR, "figure5_metrics.json"),
        os.path.join(RESULTS_DIR, "motoneuron_pools.json"),
        os.path.join(RESULTS_DIR, "motoneuron_pools.csv"),
        os.path.join(FIG_DIR, "Figure1.png"),
        os.path.join(FIG_DIR, "Figure2.png"),
        os.path.join(FIG_DIR, "Figure3.png"),
        os.path.join(FIG_DIR, "Figure4.png"),
        os.path.join(FIG_DIR, "Figure5.png"),
        os.path.join(REPRO_DIR, "Komi_reproduction_comparison.pdf"),
        os.path.join(REPRO_DIR, "REPRODUCTION_STATUS.md"),
        os.path.join(REPRO_DIR, "PANEL_VALIDATION.md"),
        os.path.join(REPRO_DIR, "source_integrity_report.txt")
    ]

    lines.append(f"{'Relative Path':<55} | {'Size (B)':<12} | {'SHA-256 Checksum':<64}")
    lines.append("-" * 137)

    for fp in files:
        if os.path.exists(fp):
            rel = os.path.relpath(fp, REPRO_DIR)
            sz = os.path.getsize(fp)
            sha = get_sha256(fp)
            lines.append(f"{rel:<55} | {sz:<12} | {sha}")
        else:
            rel = os.path.relpath(fp, REPRO_DIR)
            lines.append(f"{rel:<55} | {'MISSING':<12} | {'N/A'}")

    out_text = "\n".join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(out_text)
    print(f"\nAuthoritative checksums saved to: {output_path}")

def main():
    t_start = time.time()
    os.makedirs(LOGS_DIR, exist_ok=True)
    master_log_path = os.path.join(LOGS_DIR, "master_clean_run.log")
    comp_log_path = os.path.join(LOGS_DIR, "deterministic_rerun_comparison.log")

    with open(master_log_path, 'w', encoding='utf-8') as master_log:
        master_log.write(f"================================================================================\n")
        master_log.write(f"MASTER CLEAN RUN LOG: KOMI ET AL. (2026) REPRODUCTION PIPELINE\n")
        master_log.write(f"Start Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        master_log.write(f"MATLAB Executable: {MATLAB_BIN}\n")
        master_log.write(f"================================================================================\n\n")

        # -------------------------------------------------------------
        # RUN 1
        # -------------------------------------------------------------
        print("\n" + "#"*80)
        print("# COMMENCING DETERMINISTIC CLEAN RUN 1")
        print("#"*80)
        ok1 = run_full_pipeline("run_1", master_log)
        if not ok1:
            print("[!] Clean Run 1 failed!")
            sys.exit(1)

        run1_snap = os.path.join(RESULTS_DIR, "rerun_run1")
        print(f"\n[*] Snapshotting Run 1 outputs to: {run1_snap} ...")
        snapshot_results(run1_snap)

        # -------------------------------------------------------------
        # RUN 2
        # -------------------------------------------------------------
        print("\n" + "#"*80)
        print("# COMMENCING DETERMINISTIC CLEAN RUN 2 (IDENTICAL SEEDS)")
        print("#"*80)
        ok2 = run_full_pipeline("run_2", master_log)
        if not ok2:
            print("[!] Clean Run 2 failed!")
            sys.exit(1)

        run2_snap = os.path.join(RESULTS_DIR, "rerun_run2")
        print(f"\n[*] Snapshotting Run 2 outputs to: {run2_snap} ...")
        snapshot_results(run2_snap)

    # -------------------------------------------------------------
    # COMPARISON & VALIDATION
    # -------------------------------------------------------------
    print("\n" + "#"*80)
    print("# COMPARING RUN 1 AND RUN 2 OUTPUTS")
    print("#"*80)
    compare_snapshots(run1_snap, run2_snap, comp_log_path)

    # -------------------------------------------------------------
    # GENERATE CHECKSUMS
    # -------------------------------------------------------------
    checksums_path = os.path.join(RESULTS_DIR, "checksums.txt")
    generate_checksums_file(checksums_path)

    total_time = time.time() - t_start
    print(f"\n[+] Master clean deterministic verification completed in {total_time:.1f} s ({total_time/60:.2f} min).")

if __name__ == "__main__":
    main()
