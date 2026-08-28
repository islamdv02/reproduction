"""
Master runner script for Figure 2 of Yakovenko et al. (2002).
Generates publication plots and exports Table 1 CSV summary.
"""

import sys, os
import pandas as pd

# Add src to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from anatomy import CatLumbosacralAnatomy
from figure2_analysis import generate_figure2_complete, export_table1_csv


def main():
    print("=================================================================")
    print("  RUNNING FIGURE 2 REPRODUCTION: YAKOVENKO ET AL. (2002)")
    print("=================================================================")

    plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # 1. Initialize anatomy
    anatomy = CatLumbosacralAnatomy()

    # 2. Export Table 1
    table1_path = os.path.join(results_dir, 'table1_rostral_caudal_counts.csv')
    df_t1 = export_table1_csv(anatomy, table1_path)
    print(f"[+] Exported Table 1 verification to {table1_path}")

    # 3. Generate publication plot
    plot_path = generate_figure2_complete(output_dir=plots_dir)
    print(f"[+] Generated Figure 2 publication figure: {plot_path}")

    print("\n[OK] Figure 2 reproduction completed successfully.")


if __name__ == '__main__':
    main()
