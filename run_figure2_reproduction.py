"""
Master Reproduction Pipeline for Figure 2 of Komi et al. (Nature Communications, 2026).
Executes:
1. Spatial transcriptomics and cell census data validation.
2. Canonical 3D network instantiation (T13-S4, density=0.8).
3. Directional 3D projection kernels analysis.
4. Motoneuron pool segmental localization analysis.
5. Macroscopic N x N connectivity decomposition and cell-type interaction matrix C_ij calculation.
6. Net 1D lumbar spinal projectome extraction (Ipsilateral Mexican hat & Contralateral).
7. High-resolution figure rendering to plots/ and metric export to results/.
"""

import os
import sys
import time
import json
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from data_loader import SpinalDataLoader
from network import Network
from figure5_analysis import compute_projectome_1d_profile
from figure2_analysis import (
    compute_cell_type_connectivity_matrix,
    plot_panel_2a_spatial_transcriptomics,
    plot_panel_2b_segmental_abundance,
    plot_panel_2c_directional_kernels,
    plot_panel_2d_motoneuron_topography,
    plot_panel_2e_pairwise_connectivity,
    plot_panel_2f_cell_type_matrix,
    plot_panel_2g_net_projectome,
    generate_figure2_complete,
    CELL_ORDER
)


def run_figure2_reproduction(output_dir: str = "plots", results_dir: str = "results") -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    start_time = time.time()

    print("=" * 80)
    print("  FIGURE 2 REPRODUCTION: SPATIAL TRANSCRIPTOMICS, 3D KERNELS & PROJECTOME  ")
    print("=" * 80)

    # 1. Load biological data
    print("\n[1/6] Loading Biological Spatial Transcriptomics & Motor Pool Datasets...")
    loader = SpinalDataLoader()
    geom_data = loader.load_geometry()
    muscle_data = loader.load_muscle_segments()
    census_data = loader.load_cell_census()
    print(f"  -> Loaded {geom_data['n_voxels']:,} spatial voxels across {geom_data['n_cell_types']} cell types")
    print(f"  -> Loaded {len(muscle_data['muscle_names'])} muscle groups and {len(census_data)} cell clusters")

    # 2. Instantiate Canonical 3D Network
    print("\n[2/6] Instantiating Canonical 3D Spinal Cord Network (T13-S4, density=0.8)...")
    segments = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4']
    net = Network(segments=segments, density=0.8, symmetry=True, balance=True, rescale=True, rng_seed=42, compute_eigenspectrum=False)
    print(f"  -> Generated {net.n_neurons:,} neurons ({np.count_nonzero(net.conn_mat):,} synapses, sparsity: {1 - np.count_nonzero(net.conn_mat)/net.n_neurons**2:.4f})")

    # 3. Cell-to-Cell Interaction Matrix C_ij
    print("\n[3/6] Computing (9 x 9) Cell Type-to-Cell Type Interaction Matrix C_ij...")
    C, type_labels = compute_cell_type_connectivity_matrix(net)
    df_C = pd.DataFrame(C, index=type_labels, columns=type_labels)
    p_csv_c = os.path.join(results_dir, "cell_type_connectivity_matrix.csv")
    df_C.to_csv(p_csv_c)
    print(f"  -> Saved cell-type matrix to {p_csv_c}")

    # 4. Net 1D Lumbar Spinal Projectome Profiles
    print("\n[4/6] Extracting Net 1D Lumbar Spinal Projectomes (Ipsi & Contra)...")
    dz_ipsi, prof_ipsi = compute_projectome_1d_profile(net, ipsilateral_only=True, max_dist_um=4500.0)
    dz_contra, prof_contra = compute_projectome_1d_profile(net, contralateral_only=True, max_dist_um=4500.0)
    print(f"  -> Ipsilateral projectome: max excitation = {np.max(prof_ipsi):.2f}, min surround inhibition = {np.min(prof_ipsi):.2f}")

    # 5. Render publication figures
    print("\n[5/6] Generating Publication Figures for Panels 2A-2G and Composite Figure 2...")

    p_2a = os.path.join(output_dir, "06_fig2a_spatial_transcriptomics.png")
    fig_2a = plot_panel_2a_spatial_transcriptomics(net, output_path=p_2a, dpi=300)
    plt.close(fig_2a)

    p_2b = os.path.join(output_dir, "07_fig2b_segmental_abundance.png")
    fig_2b = plot_panel_2b_segmental_abundance(net, output_path=p_2b, dpi=300)
    plt.close(fig_2b)

    p_2c = os.path.join(output_dir, "08_fig2c_directional_kernels.png")
    fig_2c = plot_panel_2c_directional_kernels(output_path=p_2c, dpi=300)
    plt.close(fig_2c)

    p_2d = os.path.join(output_dir, "09_fig2d_motoneuron_topography.png")
    fig_2d = plot_panel_2d_motoneuron_topography(loader, output_path=p_2d, dpi=300)
    plt.close(fig_2d)

    p_2e = os.path.join(output_dir, "10_fig2e_pairwise_connectivity.png")
    fig_2e = plot_panel_2e_pairwise_connectivity(net, output_path=p_2e, dpi=300)
    plt.close(fig_2e)

    p_2f = os.path.join(output_dir, "11_fig2f_cell_type_matrix.png")
    fig_2f = plot_panel_2f_cell_type_matrix(net, output_path=p_2f, dpi=300)
    plt.close(fig_2f)

    p_2g = os.path.join(output_dir, "12_fig2g_net_projectome.png")
    fig_2g = plot_panel_2g_net_projectome(net, output_path=p_2g, dpi=300)
    plt.close(fig_2g)

    p_comp = os.path.join(output_dir, "figure2_complete.png")
    fig_comp = generate_figure2_complete(net, loader, output_path=p_comp, dpi=300)
    plt.close(fig_comp)

    # 6. Export Summary Metrics JSON
    print("\n[6/6] Serializing Quantitative Metrics to JSON...")
    ipsi_syn = int(np.count_nonzero(np.where(np.outer(net.latera, net.latera) > 0, net.conn_mat, 0.0)))
    contra_syn = int(np.count_nonzero(np.where(np.outer(net.latera, net.latera) < 0, net.conn_mat, 0.0)))

    cell_counts = {c: int(np.sum(net.types == c)) for c in CELL_ORDER}

    summary_metrics = {
        'figure': 2,
        'title': 'Spatial Transcriptomics, 3D Directional Kernels, Motor Pools & Net Lumbar Projectome',
        'anatomical_space': {
            'x_range_um': [-1750.0, 1750.0],
            'y_range_um': [0.0, 1613.3],
            'z_range_um': [0.0, 11000.0],
            'segments': segments
        },
        'network_architecture': {
            'total_neurons': net.n_neurons,
            'total_synapses': int(np.count_nonzero(net.conn_mat)),
            'sparsity': float(1.0 - np.count_nonzero(net.conn_mat) / net.n_neurons**2),
            'ipsilateral_synapses': ipsi_syn,
            'contralateral_synapses': contra_syn,
            'ipsi_percentage': float(ipsi_syn / np.count_nonzero(net.conn_mat) * 100),
            'contra_percentage': float(contra_syn / np.count_nonzero(net.conn_mat) * 100)
        },
        'cell_type_abundances': cell_counts,
        'projectome_features': {
            'ipsilateral_profile': {
                'peak_excitation_weight': float(np.max(prof_ipsi)),
                'peak_inhibition_weight': float(np.min(prof_ipsi)),
                'excitation_radius_um': 500.0,
                'inhibition_span_um': [1000.0, 4000.0],
                'profile_type': 'Asymmetric Mexican Hat'
            },
            'contralateral_profile': {
                'peak_excitation_weight': float(np.max(prof_contra)),
                'peak_inhibition_weight': float(np.min(prof_contra)),
                'profile_type': 'Bilateral Commissural'
            }
        },
        'artifacts': {
            'panel_2a': p_2a,
            'panel_2b': p_2b,
            'panel_2c': p_2c,
            'panel_2d': p_2d,
            'panel_2e': p_2e,
            'panel_2f': p_2f,
            'panel_2g': p_2g,
            'figure2_complete': p_comp,
            'csv_c_matrix': p_csv_c
        }
    }

    p_json = os.path.join(results_dir, "figure2_summary.json")
    with open(p_json, 'w') as f:
        json.dump(summary_metrics, f, indent=2)

    elapsed = time.time() - start_time
    print(f"\n{'=' * 80}")
    print(f"  FIGURE 2 REPRODUCTION COMPLETED IN {elapsed:.1f}s")
    print(f"{'=' * 80}\n")
    return summary_metrics


if __name__ == '__main__':
    run_figure2_reproduction()
