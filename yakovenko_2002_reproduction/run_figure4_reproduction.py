"""
Master runner script for Figure 4 of Yakovenko et al. (2002).
Generates publication plots and exports 3D activity grid NPZ.
"""

import sys, os

# Add src to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from anatomy import CatLumbosacralAnatomy
from emg_profiles import CatHindlimbEMG
from spatiotemporal_model import SpatiotemporalModel
from figure4_analysis import generate_figure4_complete, export_figure4_data


def main():
    print("=================================================================")
    print("  RUNNING FIGURE 4 REPRODUCTION: YAKOVENKO ET AL. (2002)")
    print("=================================================================")

    plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # 1. Initialize and run model
    anatomy = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)
    model = SpatiotemporalModel(anatomy=anatomy, emg=emg, recruitment_mode='graded',
                                fdl_as_retractor=True, n_cycles=2)

    # 2. Export NPZ grid
    npz_path = os.path.join(results_dir, 'figure4_spatiotemporal_grid.npz')
    export_figure4_data(model, npz_path)
    print(f"[+] Exported 3D activity grid to {npz_path}")

    # 3. Generate publication plot
    plot_path = generate_figure4_complete(output_dir=plots_dir)
    print(f"[+] Generated Figure 4 publication figure: {plot_path}")

    print("\n[OK] Figure 4 reproduction completed successfully.")


if __name__ == '__main__':
    main()
