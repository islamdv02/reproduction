"""
Figure 2 Analysis: Rostrocaudal Motoneuron Distributions and Table 1 Validation.
Faithfully reproduces Figure 2 (Panels 2A, 2B, 2C) and Table 1 from Yakovenko et al. (2002).
"""

import os
from typing import Dict, Tuple
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from anatomy import CatLumbosacralAnatomy, MUSCLE_NAMES, MUSCLE_CATEGORIES


def compute_figure2_distributions(anatomy: CatLumbosacralAnatomy):
    """
    Computes slice-wise distributions across 30 slices for:
    - Total MNs
    - Flexor MNs
    - Extensor MNs (with and without FDL)
    - Retractor MNs (with and without FDL)
    """
    slices = np.arange(anatomy.n_slices)
    levels = anatomy.slice_centers_level

    total_mns = np.sum(anatomy.slice_matrix, axis=0)

    # Flexors (Psoas, Iliacus, SRTa, SRTm, TA, EDL)
    flexor_idx = [i for i, m in enumerate(MUSCLE_NAMES) if MUSCLE_CATEGORIES[m] == 'flexor']
    flexor_dist = np.sum(anatomy.slice_matrix[flexor_idx, :], axis=0)

    # Extensors (with and without FDL)
    ext_idx_no_fdl = [i for i, m in enumerate(MUSCLE_NAMES) if MUSCLE_CATEGORIES[m] == 'extensor']
    ext_dist_no_fdl = np.sum(anatomy.slice_matrix[ext_idx_no_fdl, :], axis=0)

    fdl_idx = MUSCLE_NAMES.index('FDL')
    ext_dist_with_fdl = ext_dist_no_fdl + anatomy.slice_matrix[fdl_idx, :]

    # Retractors (with and without FDL)
    ret_idx_with_fdl = [i for i, m in enumerate(MUSCLE_NAMES) if MUSCLE_CATEGORIES[m] == 'retractor']
    ret_dist_with_fdl = np.sum(anatomy.slice_matrix[ret_idx_with_fdl, :], axis=0)

    ret_idx_no_fdl = [i for i in ret_idx_with_fdl if i != fdl_idx]
    ret_dist_no_fdl = np.sum(anatomy.slice_matrix[ret_idx_no_fdl, :], axis=0)

    return {
        'levels': levels,
        'slices': slices,
        'total': total_mns,
        'flexor': flexor_dist,
        'extensor_no_fdl': ext_dist_no_fdl,
        'extensor_with_fdl': ext_dist_with_fdl,
        'retractor_with_fdl': ret_dist_with_fdl,
        'retractor_no_fdl': ret_dist_no_fdl
    }


def generate_figure2_complete(output_dir: str = "plots") -> str:
    """Generates the master composite Figure 2 publication layout matching the paper."""
    os.makedirs(output_dir, exist_ok=True)
    anatomy = CatLumbosacralAnatomy()
    dists = compute_figure2_distributions(anatomy)

    fig, axes = plt.subplots(3, 1, figsize=(6.5, 8.5), dpi=300, sharex=True)
    fig.suptitle("Figure 2: MN Distribution Along Rostrocaudal Axis of Lumbar Enlargement",
                 fontsize=11.5, fontweight='bold', y=0.98)

    levels = dists['levels']
    total = dists['total']

    # Segment labels and positions
    seg_labels = [('~L4', 6.6), ('~L5', 23.3), ('~L6', 46.6), ('~L7', 73.3), ('~S1', 93.3)]

    # --- Panel 2A: Flexor Motoneurons ---
    ax_a = axes[0]
    ax_a.plot(levels, total, '--', color='#555555', linewidth=1.2, label='all motoneurons')
    ax_a.plot(levels, dists['flexor'], '-', color='#1f77b4', linewidth=2.0, label='flexor motoneurons')
    ax_a.set_ylabel("number of motoneurons\nper section", fontsize=9)
    ax_a.set_ylim(0, 300)
    ax_a.set_yticks([0, 150, 300])
    ax_a.text(-0.15, 0.95, 'A', transform=ax_a.transAxes, fontsize=13, fontweight='bold', va='top')
    ax_a.legend(loc='upper right', frameon=False, fontsize=8.5)

    # --- Panel 2B: Extensor Motoneurons ---
    ax_b = axes[1]
    ax_b.plot(levels, total, '--', color='#555555', linewidth=1.2, label='all motoneurons')
    ax_b.plot(levels, dists['extensor_no_fdl'], '-', color='#d62728', linewidth=2.0, label='extensor motoneurons without FDL')
    ax_b.plot(levels, dists['extensor_with_fdl'], ':', color='#d62728', linewidth=2.0, label='extensor motoneurons with FDL')
    ax_b.set_ylabel("number of motoneurons\nper section", fontsize=9)
    ax_b.set_ylim(0, 300)
    ax_b.set_yticks([0, 150, 300])
    ax_b.text(-0.15, 0.95, 'B', transform=ax_b.transAxes, fontsize=13, fontweight='bold', va='top')
    ax_b.legend(loc='upper left', frameon=False, fontsize=8.5)

    # --- Panel 2C: Retractor Motoneurons ---
    ax_c = axes[2]
    ax_c.plot(levels, total, '--', color='#555555', linewidth=1.2, label='all motoneurons')
    ax_c.plot(levels, dists['retractor_with_fdl'], '-', color='#2ca02c', linewidth=2.0, label='BFp, FDL, Gracilis, SMP, ST')
    ax_c.plot(levels, dists['retractor_no_fdl'], ':', color='#2ca02c', linewidth=2.0, label='BFp, Gracilis, SMP, ST')
    ax_c.set_ylabel("number of motoneurons\nper section", fontsize=9)
    ax_c.set_xlabel("level", fontsize=9.5)
    ax_c.set_ylim(0, 300)
    ax_c.set_yticks([0, 150, 300])
    ax_c.set_xlim(0, 100)
    ax_c.set_xticks([0, 50, 100])
    ax_c.text(-0.15, 0.95, 'C', transform=ax_c.transAxes, fontsize=13, fontweight='bold', va='top')
    ax_c.legend(loc='upper left', frameon=False, fontsize=8.5)

    # Add segment indicators below Panel C
    for seg, pos in seg_labels:
        ax_c.text(pos, -45, seg, ha='center', va='top', fontsize=8, color='#333333', clip_on=False)

    for ax in axes:
        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    out_path = os.path.join(output_dir, "figure2_mn_distributions.png")
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out_path


def export_table1_csv(anatomy: CatLumbosacralAnatomy, output_path: str):
    """Exports Table 1 quantitative counts and percentages to CSV."""
    t1 = anatomy.get_table1_counts(fdl_as_retractor=True)
    df = pd.DataFrame([
        {
            'Group': 'Extensor Motoneurons',
            'Rostral_Count': t1['extensor']['rostral'],
            'Rostral_Pct': round(t1['extensor']['rostral'] / t1['extensor']['total'] * 100, 1),
            'Caudal_Count': t1['extensor']['caudal'],
            'Caudal_Pct': round(t1['extensor']['caudal'] / t1['extensor']['total'] * 100, 1),
            'Full_Total': t1['extensor']['total']
        },
        {
            'Group': 'BFp, FDL, Gracilis, SMp, ST (Retractors)',
            'Rostral_Count': t1['retractor']['rostral'],
            'Rostral_Pct': round(t1['retractor']['rostral'] / t1['retractor']['total'] * 100, 1),
            'Caudal_Count': t1['retractor']['caudal'],
            'Caudal_Pct': round(t1['retractor']['caudal'] / t1['retractor']['total'] * 100, 1),
            'Full_Total': t1['retractor']['total']
        },
        {
            'Group': 'Flexor Motoneurons',
            'Rostral_Count': t1['flexor']['rostral'],
            'Rostral_Pct': round(t1['flexor']['rostral'] / t1['flexor']['total'] * 100, 1),
            'Caudal_Count': t1['flexor']['caudal'],
            'Caudal_Pct': round(t1['flexor']['caudal'] / t1['flexor']['total'] * 100, 1),
            'Full_Total': t1['flexor']['total']
        },
        {
            'Group': 'All Motoneurons',
            'Rostral_Count': t1['all']['rostral'],
            'Rostral_Pct': round(t1['all']['rostral'] / t1['all']['total'] * 100, 1),
            'Caudal_Count': t1['all']['caudal'],
            'Caudal_Pct': round(t1['all']['caudal'] / t1['all']['total'] * 100, 1),
            'Full_Total': t1['all']['total']
        }
    ])
    df.to_csv(output_path, index=False)
    return df
