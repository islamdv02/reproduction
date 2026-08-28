"""
Figure 1 Analysis: Anatomical Models of Cat Lumbosacral Motoneuron Pools.
Visualizes the 3D organization of MN pools partitioned into Hip, Knee, and Ankle groups,
including rostrocaudal extent bars, centers of mass, and unit oscillator distances.
"""

import os
from typing import Dict, List, Optional
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
from anatomy import CatLumbosacralAnatomy, MUSCLE_NAMES, JOINT_GROUPS, MUSCLE_CATEGORIES

# Color map for anatomical pools
POOL_COLORS = {
    'Psoas': '#2ca02c', 'Iliacus': '#3caea3', 'SRTa': '#17becf', 'SRTm': '#1f77b4',
    'RF': '#9467bd', 'VL': '#d62728', 'VM': '#ff7f0e', 'VI': '#e377c2',
    'TA': '#8c564b', 'EDL': '#bcbd22',
    'AdFM': '#7f7f7f', 'Gracilis': '#2ca02c', 'SMa': '#ffbb78',
    'GlutMed': '#aec7e8', 'CF': '#98df8a', 'BFa': '#ff9896', 'GlutMax': '#c5b0d5',
    'BFp': '#c49c94', 'ST': '#f7b6d2', 'SMp': '#dbdb8d',
    'FDL': '#9edae5', 'FHL': '#393b79', 'Plantaris': '#637939', 'Soleus': '#8c6d31',
    'LG': '#843c39', 'MG': '#7b4173', 'TP': '#5254a3'
}


def plot_figure1_joint_group(ax_bar, ax_3d, joint: str, anatomy: CatLumbosacralAnatomy):
    """Plots the rostrocaudal bars and 3D schematic for a specific joint group (hip, knee, ankle)."""
    muscles = JOINT_GROUPS[joint]

    # 1. Plot Rostrocaudal extent bars on ax_bar
    ax_bar.set_ylim(105, -5) # Rostral at top (0), Caudal at bottom (100)
    ax_bar.set_xlim(-0.5, len(muscles) + 0.5)

    for idx, m in enumerate(muscles):
        r_lvl = anatomy.rostral_extent_level[m]
        c_lvl = anatomy.caudal_extent_level[m]
        cm_lvl = anatomy.centers_of_mass_level[m]
        col = POOL_COLORS.get(m, '#333333')

        # Vertical extent bar
        rect = patches.Rectangle((idx - 0.35, r_lvl), 0.7, max(c_lvl - r_lvl, 2.0),
                                 facecolor=col, edgecolor='black', alpha=0.8, linewidth=0.8)
        ax_bar.add_patch(rect)

        # Center of mass circle
        ax_bar.plot(idx, cm_lvl, 'o', color='white', markeredgecolor='black', markersize=5, markeredgewidth=1.2)

        # Text label
        cat = MUSCLE_CATEGORIES[m]
        style = 'bold' if cat in ['retractor', 'flexor'] else 'normal'
        ax_bar.text(idx, c_lvl + 2.5, m, rotation=90, ha='center', va='top', fontsize=7.5, fontweight=style)

    ax_bar.set_title(f"{joint.capitalize()} Pools", fontsize=11, fontweight='bold', pad=10)
    ax_bar.set_ylabel("Spinal Cord Level (0 = L4, 100 = S1)", fontsize=8.5)
    ax_bar.set_xticks([])

    # Add segmental boundary indicators
    seg_bounds = [('~L4', 0), ('~L5', 13.3), ('~L6', 33.3), ('~L7', 60.0), ('~S1', 86.7), ('', 100.0)]
    for seg, lvl in seg_bounds:
        ax_bar.axhline(lvl, color='#dddddd', linestyle='--', linewidth=0.6, zorder=0)
        if seg:
            ax_bar.text(-0.45, lvl + 2, seg, fontsize=7, color='#555555', ha='left')

    # 2. Plot 3D Spinal Cord Surface / Column schematic on ax_3d
    z = np.linspace(0, 28.8, 100)
    # Gray matter outline boundary
    gm_width = 3.6 * np.ones_like(z)
    gm_dv = 5.5 * np.ones_like(z)

    # Plot gray matter envelope
    ax_3d.plot(np.zeros_like(z), np.zeros_like(z), z, color='gray', linestyle=':', alpha=0.5)

    for m in muscles:
        counts = np.array(anatomy.df_distribution.loc[m], dtype=np.float64)
        active_idx = np.where(counts > 0)[0]
        if len(active_idx) > 0:
            z_m = anatomy.slice_centers_mm[active_idx]
            cnt_m = counts[active_idx]
            # Mediolateral offset based on muscle
            x_m = 0.5 * np.sin(np.linspace(0, np.pi, len(z_m))) + (hash(m) % 5 - 2) * 0.3
            y_m = 0.5 * np.cos(np.linspace(0, np.pi, len(z_m))) + (hash(m) % 7 - 3) * 0.3
            col = POOL_COLORS.get(m, '#333333')
            ax_3d.plot(x_m, y_m, z_m, color=col, linewidth=2.2, alpha=0.85, label=m)

    ax_3d.set_zlim(28.8, 0) # Invert Z to match rostral top
    ax_3d.set_xlim(-2.5, 2.5)
    ax_3d.set_ylim(-2.5, 2.5)
    ax_3d.set_xlabel("ML (mm)", fontsize=6.5, labelpad=-10)
    ax_3d.set_ylabel("DV (mm)", fontsize=6.5, labelpad=-10)
    ax_3d.set_zlabel("RC (mm)", fontsize=6.5, labelpad=-10)
    ax_3d.tick_params(labelsize=6)
    ax_3d.view_init(elev=20, azim=45)


def generate_figure1_complete(output_dir: str = "plots") -> str:
    """Generates the master composite Figure 1 publication layout."""
    os.makedirs(output_dir, exist_ok=True)
    anatomy = CatLumbosacralAnatomy()

    fig = plt.figure(figsize=(14, 8), dpi=300)
    fig.suptitle("Figure 1: Anatomical Models of Cat Lumbosacral Motoneuron Pools (L4 - S1)",
                 fontsize=13, fontweight='bold', y=0.98)

    # 3 Joint groups: Hip, Knee, Ankle
    joints = ['hip', 'knee', 'ankle']
    for i, j in enumerate(joints):
        # Top subplot: Bar schematic
        ax_bar = fig.add_subplot(2, 3, i + 1)
        # Bottom subplot: 3D schematic
        ax_3d = fig.add_subplot(2, 3, i + 4, projection='3d')

        plot_figure1_joint_group(ax_bar, ax_3d, j, anatomy)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(output_dir, "figure1_mn_pool_anatomy.png")
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out_path


def compute_figure1_metrics(anatomy: CatLumbosacralAnatomy) -> pd.DataFrame:
    """Computes centers of mass and rostrocaudal spans for all 27 muscles."""
    records = []
    for m in MUSCLE_NAMES:
        records.append({
            'muscle': m,
            'category': MUSCLE_CATEGORIES[m],
            'total_mns': int(np.sum(anatomy.df_distribution.loc[m])),
            'center_of_mass_level': round(anatomy.centers_of_mass_level[m], 2),
            'center_of_mass_mm': round(anatomy.centers_of_mass_mm[m], 2),
            'rostral_extent_level': round(anatomy.rostral_extent_level[m], 2),
            'caudal_extent_level': round(anatomy.caudal_extent_level[m], 2)
        })
    df = pd.DataFrame(records)
    return df
