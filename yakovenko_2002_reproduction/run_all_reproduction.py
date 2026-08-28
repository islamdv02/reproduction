"""
Master Execution Pipeline for Complete Yakovenko et al. (2002) Reproduction.
Executes Figures 1-5, generates all publication plots and exported datasets.
"""

import sys, os
import subprocess

def main():
    print("========================================================================")
    print("  STARTING FULL COMPUTATIONAL REPRODUCTION: YAKOVENKO ET AL. (2002)     ")
    print("  'Spatiotemporal Activation of Lumbosacral Motoneurons in Locomotion'  ")
    print("========================================================================")

    root_dir = os.path.dirname(__file__)

    scripts = [
        "run_figure1_reproduction.py",
        "run_figure2_reproduction.py",
        "run_figure3_reproduction.py",
        "run_figure4_reproduction.py",
        "run_figure5_reproduction.py"
    ]

    for script in scripts:
        script_path = os.path.join(root_dir, script)
        print(f"\n---> Executing {script}...")
        res = subprocess.run([sys.executable, script_path], cwd=root_dir, capture_output=True, text=True)
        print(res.stdout)
        if res.returncode != 0:
            print(f"[ERROR] Script {script} failed with exit code {res.returncode}:")
            print(res.stderr)
            sys.exit(res.returncode)

    print("\n========================================================================")
    print("  [SUCCESS] All Figures 1-5 reproduced and verified successfully!       ")
    print("========================================================================")

if __name__ == '__main__':
    main()
