"""
Figure 4 Analysis: 3D Spatiotemporal Landscape of Motoneuron Activity.
Faithfully reproduces Figure 4 from Yakovenko et al. (J Neurophysiol 2002).
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from anatomy import CatLumbosacralAnatomy
from emg_profiles import CatHindlimbEMG
from spatiotemporal_model import SpatiotemporalModel


def generate_figure4_complete(output_dir: str = "plots") -> str:
    """Generates the master 3D surface plot matching Figure 4 over 2 step cycles."""
    os.makedirs(output_dir, exist_ok=True)
    anatomy = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)
    model = SpatiotemporalModel(anatomy=anatomy, emg=emg, recruitment_mode='graded',
                                fdl_as_retractor=True, n_cycles=2)

    # Activity grid: (30 slices x 200 time bins)
    grid = model.activity_grid

    # Coordinate meshes
    t_vals = np.linspace(0, 200, 200)
    level_vals = anatomy.slice_centers_level
    T, L = np.meshgrid(t_vals, level_vals)

    fig = plt.figure(figsize=(10, 7.5), dpi=300)
    ax = fig.add_subplot(111, projection='3d')

    # Render surface
    surf = ax.plot_surface(T, L, grid, cmap=cm.jet, edgecolor='none', alpha=0.9, antialiased=True, rstride=1, cstride=1)

    # Annotations and axis labels
    ax.set_title("Figure 4: Modeled Spinal MN Activity in the Lumbosacral Enlargement During Locomotion",
                 fontsize=11, fontweight='bold', pad=20)

    ax.set_xlabel("step cycle, %", fontsize=9.5, labelpad=10)
    ax.set_ylabel("level", fontsize=9.5, labelpad=10)
    ax.set_zlabel("number of motoneurons", fontsize=9.5, labelpad=8)

    ax.set_xlim(0, 200)
    ax.set_xticks([0, 50, 100, 150, 200])

    ax.set_ylim(0, 100)
    ax.set_yticks([0, 50, 100])
    ax.set_yticklabels(['0\n~L4', '50\n~L6', '100\n~S1'])

    max_z = np.max(grid)
    ax.set_zlim(0, max_z * 1.15)

    # Add phase labels above plot
    # Cycle 1: swing 0-30, stance 30-100
    # Cycle 2: swing 100-130, stance 130-200
    ax.text(15, 0, max_z * 1.05, "swing", ha='center', fontsize=9, style='italic', color='#333333')
    ax.text(65, 0, max_z * 1.05, "stance", ha='center', fontsize=9, style='italic', color='#333333')
    ax.text(115, 0, max_z * 1.05, "swing", ha='center', fontsize=9, style='italic', color='#333333')
    ax.text(165, 0, max_z * 1.05, "stance", ha='center', fontsize=9, style='italic', color='#333333')

    # Adjust 3D view angle to match Figure 4 perspective
    ax.view_init(elev=35, azim=-125)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "figure4_spatiotemporal_activity.png")
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out_path


def export_figure4_data(model: SpatiotemporalModel, output_path: str):
    """Exports the 30x200 activity grid to NPZ for quantitative records."""
    np.savez(output_path, activity_grid=model.activity_grid,
             r_cm_level=model.r_cm_level, r_cm_mm=model.r_cm_mm,
             velocity_mm_s=model.velocity_mm_s)
