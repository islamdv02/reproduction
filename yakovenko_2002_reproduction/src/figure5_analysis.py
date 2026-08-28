"""
Figure 5 Analysis: Parametric Sensitivity of Lumbosacral Motoneuron Activation.
Faithfully reproduces Figure 5 (Panels 5A, 5B, 5C, 5D) from Yakovenko et al. (J Neurophysiol 2002).
"""

import os
from typing import Dict, Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
from anatomy import CatLumbosacralAnatomy
from emg_profiles import CatHindlimbEMG
from spatiotemporal_model import SpatiotemporalModel


def plot_figure5_panel(ax, model: SpatiotemporalModel, title: str, panel_letter: str, show_arrows: bool = False):
    """Plots a single plan-view heatmap of the activity grid with center-of-mass overlay."""
    grid = model.activity_grid
    r_cm_level = model.r_cm_level
    n_slices, n_bins = grid.shape

    t_vals = np.linspace(0, 200, n_bins)
    level_vals = model.anatomy.slice_centers_level

    # 2D Heatmap (imshow with extent)
    # Origin at top (level 0), bottom at level 100
    im = ax.imshow(grid, aspect='auto', origin='upper', cmap='turbo',
                   extent=[0, 200, 100, 0], interpolation='nearest')

    # Overlay center of mass trajectory (open circles)
    ax.plot(t_vals, r_cm_level, 'o', color='white', markeredgecolor='black',
            markersize=3.2, markeredgewidth=0.8, alpha=0.9, zorder=5)

    # Segment indicator lines
    seg_bounds = [('~L4', 0), ('~L5', 13.3), ('~L6', 33.3), ('~L7', 60.0), ('~S1', 86.7), ('', 100.0)]
    for seg, lvl in seg_bounds:
        ax.axhline(lvl, color='white', linestyle='--', linewidth=0.5, alpha=0.5)
        if seg:
            ax.text(2, lvl + 4, seg, fontsize=7, color='white', fontweight='bold', va='top')

    # Add phase headers above
    ax.text(15, -6, "swing", ha='center', fontsize=8, style='italic', color='#333333')
    ax.text(65, -6, "stance", ha='center', fontsize=8, style='italic', color='#333333')
    ax.text(115, -6, "swing", ha='center', fontsize=8, style='italic', color='#333333')
    ax.text(165, -6, "stance", ha='center', fontsize=8, style='italic', color='#333333')

    # Annotation arrows on Panel 5A
    if show_arrows:
        # Arrow a: Caudal movement at stance-swing transition (around t=96-100)
        ax.annotate('a', xy=(95, 78), xytext=(85, 65),
                    arrowprops=dict(facecolor='white', edgecolor='black', arrowstyle='->', lw=1.2),
                    fontsize=9, fontweight='bold', color='white')
        # Arrow b: Activity in BFp, Gracilis, SMp, ST
        ax.annotate('b', xy=(98, 88), xytext=(108, 95),
                    arrowprops=dict(facecolor='white', edgecolor='black', arrowstyle='->', lw=1.2),
                    fontsize=9, fontweight='bold', color='white')
        # Arrow c: Activity in FDL
        ax.annotate('c', xy=(94, 68), xytext=(80, 50),
                    arrowprops=dict(facecolor='white', edgecolor='black', arrowstyle='->', lw=1.2),
                    fontsize=9, fontweight='bold', color='white')

    ax.set_title(f"{panel_letter} {title}", fontsize=9.5, fontweight='bold', pad=18, loc='left')
    ax.set_xlabel("step cycle, %", fontsize=8.5)
    ax.set_ylabel("level", fontsize=8.5)
    ax.set_xlim(0, 200)
    ax.set_xticks([0, 50, 100, 150, 200])
    ax.set_ylim(100, 0) # Inverted: level 0 at top
    ax.set_yticks([0, 50, 100])

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    max_val = int(np.round(np.max(grid)))
    cbar.set_ticks([0, max_val])
    cbar.set_label("number of motoneurons", fontsize=7.5, rotation=270, labelpad=10)
    cbar.ax.tick_params(labelsize=7)


def generate_figure5_complete(output_dir: str = "plots") -> str:
    """Generates the master 4-panel composite Figure 5 publication layout."""
    os.makedirs(output_dir, exist_ok=True)
    anatomy = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)

    # 4 simulation conditions
    m_5a = SpatiotemporalModel(anatomy=anatomy, emg=emg, recruitment_mode='graded', n_cycles=2)
    m_5b = SpatiotemporalModel(anatomy=anatomy, emg=emg, recruitment_mode='step', n_cycles=2)
    m_5c = SpatiotemporalModel(anatomy=anatomy, emg=emg, recruitment_mode='phys_40_15', n_cycles=2)
    m_5d = SpatiotemporalModel(anatomy=anatomy, emg=emg, recruitment_mode='inv_15_40', n_cycles=2)

    fig, axes = plt.subplots(2, 2, figsize=(13, 10), dpi=300)
    fig.suptitle("Figure 5: Variations in Assumed Activation Patterns to Assess Parametric Sensitivity",
                 fontsize=12, fontweight='bold', y=0.98)

    plot_figure5_panel(axes[0, 0], m_5a, "flexors-retractors-extensors: 100% (graded)", "A", show_arrows=True)
    plot_figure5_panel(axes[0, 1], m_5b, "flexors-retractors-extensors: 100% (all-or-nothing)", "B", show_arrows=False)
    plot_figure5_panel(axes[1, 0], m_5c, "flexors-retractors: 15%, extensors: 40% (graded)", "C", show_arrows=False)
    plot_figure5_panel(axes[1, 1], m_5d, "flexors-retractors: 40%, extensors: 15% (graded)", "D", show_arrows=False)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(output_dir, "figure5_parametric_sensitivity.png")
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out_path


def export_figure5_trajectories_csv(models: Dict[str, SpatiotemporalModel], output_path: str):
    """Exports center of mass timeseries and velocities across all 4 modes to CSV."""
    records = []
    for t in range(100):
        rec = {'step_cycle_pct': t}
        for name, m in models.items():
            rec[f'r_cm_level_{name}'] = round(m.r_cm_level[t], 2)
            rec[f'r_cm_mm_{name}'] = round(m.r_cm_mm[t], 2)
            rec[f'velocity_mm_s_{name}'] = round(m.velocity_mm_s[t], 2)
        records.append(rec)
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    return df
