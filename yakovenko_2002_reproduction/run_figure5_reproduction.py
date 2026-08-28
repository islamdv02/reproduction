"""
Master runner script for Figure 5 of Yakovenko et al. (2002).
Generates publication plots of 4 parametric sensitivity modes and exports trajectories CSV.
"""

import sys, os

# Add src to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from anatomy import CatLumbosacralAnatomy
from emg_profiles import CatHindlimbEMG
from spatiotemporal_model import SpatiotemporalModel
from figure5_analysis import generate_figure5_complete, export_figure5_trajectories_csv


def main():
    print("=================================================================")
    print("  RUNNING FIGURE 5 REPRODUCTION: YAKOVENKO ET AL. (2002)")
    print("=================================================================")

    plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    anatomy = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)

    # 1. Run 4 models
    models = {
        '5A_graded': SpatiotemporalModel(anatomy=anatomy, emg=emg, recruitment_mode='graded', n_cycles=1),
        '5B_step': SpatiotemporalModel(anatomy=anatomy, emg=emg, recruitment_mode='step', n_cycles=1),
        '5C_phys_40_15': SpatiotemporalModel(anatomy=anatomy, emg=emg, recruitment_mode='phys_40_15', n_cycles=1),
        '5D_inv_15_40': SpatiotemporalModel(anatomy=anatomy, emg=emg, recruitment_mode='inv_15_40', n_cycles=1),
    }

    # 2. Export trajectory timeseries
    csv_path = os.path.join(results_dir, 'figure5_center_of_mass_trajectories.csv')
    export_figure5_trajectories_csv(models, csv_path)
    print(f"[+] Exported center of mass trajectories to {csv_path}")

    # 3. Generate publication plot
    plot_path = generate_figure5_complete(output_dir=plots_dir)
    print(f"[+] Generated Figure 5 publication figure: {plot_path}")

    print("\n[OK] Figure 5 reproduction completed successfully.")


if __name__ == '__main__':
    main()
