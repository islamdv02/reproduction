"""
Master runner script for Figure 1 of Yakovenko et al. (2002).
Generates publication plots and CSV summary of pool metrics.
"""

import sys, os
import pandas as pd

# Add src to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from anatomy import CatLumbosacralAnatomy
from figure1_analysis import generate_figure1_complete, compute_figure1_metrics


def main():
    print("=================================================================")
    print("  RUNNING FIGURE 1 REPRODUCTION: YAKOVENKO ET AL. (2002)")
    print("=================================================================")

    plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # 1. Initialize anatomy
    anatomy = CatLumbosacralAnatomy()

    # 2. Compute metrics
    df_metrics = compute_figure1_metrics(anatomy)
    csv_path = os.path.join(results_dir, 'figure1_pool_centers_of_mass.csv')
    df_metrics.to_csv(csv_path, index=False)
    print(f"[+] Exported Figure 1 pool metrics to {csv_path}")

    # 3. Generate publication plot
    plot_path = generate_figure1_complete(output_dir=plots_dir)
    print(f"[+] Generated Figure 1 publication figure: {plot_path}")

    print("\n[OK] Figure 1 reproduction completed successfully.")


if __name__ == '__main__':
    main()
