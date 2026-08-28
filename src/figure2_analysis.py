"""
Figure 2 Analysis and Visualization Module.
Reproduces Figure 2 from Komi et al. (Nature Communications, 2026):
- Panel 2A: Spatial transcriptomics & cell census mapping across transverse Rexed laminae.
- Panel 2B: Segmental distribution & cardinal population abundance across T13-S4.
- Panel 2C: 3D anisotropic Gaussian projection kernels along RC, ML, and DV axes.
- Panel 2D: Motoneuron pool segmental topography (Flexor vs Extensor segregation).
- Panel 2E: Full N x N pairwise connectivity matrix with zoom-in and Ipsi/Contra decomposition.
- Panel 2F: Normalized (9 x 9) Cell Type-to-Cell Type interaction matrix C_ij.
- Panel 2G: Macroscopic net lumbar spinal projectome profiles (Ipsilateral Mexican hat vs Contralateral).
- Complete Composite Figure 2.
"""

import os
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

CELL_COLORS = {
    'V2a-2': '#2ca02c',  # Green (Excitatory Descending)
    'V2a-1': '#98df8a',  # Light Green (Excitatory Local)
    'V1':    '#1f77b4',  # Blue (Inhibitory Local/Rostral)
    'V2b':   '#aec7e8',  # Light Blue (Inhibitory Caudal)
    'V0v':   '#9467bd',  # Purple (Commissural Excitatory)
    'V0d':   '#c5b0d5',  # Light Purple (Commissural Inhibitory)
    'V3':    '#ff7f0e',  # Orange (Commissural Excitatory)
    'dI6':   '#ffbb78',  # Light Orange (Commissural Inhibitory)
    'MN':    '#d62728'   # Red (Motoneurons)
}

CELL_ORDER = ['V2a-2', 'V2a-1', 'V1', 'V2b', 'V0v', 'V0d', 'V3', 'dI6', 'MN']


def get_neuron_segments(net: Any) -> np.ndarray:
    """Computes spinal segment for each neuron based on pos_z and segment lengths."""
    geom_data = net.data_loader.load_geometry()
    seg_names = geom_data['segment_names']
    seg_lens = geom_data['segment_lengths_um']
    
    seg_dict = {s: seg_lens[seg_names.index(s)] for s in net.segments if s in seg_names}
    bounds = np.insert(np.cumsum([seg_dict.get(s, 1000.0) for s in net.segments]), 0, 0.0)
    
    seg_indices = np.clip(np.digitize(net.pos_z, bounds) - 1, 0, len(net.segments) - 1)
    return np.array([net.segments[i] for i in seg_indices])


def compute_cell_type_connectivity_matrix(net: Any) -> Tuple[np.ndarray, List[str]]:
    """
    Computes the normalized (9 x 9) Cell Type-to-Cell Type connectivity matrix C_ij:
      C_{ij} = sum_{k in type i, l in type j} |w_{kl}| / sum_{k in type i} sum_l |w_{kl}|
    where row i is postsynaptic target type and column j is presynaptic source type.
    """
    W = np.abs(net.conn_mat)
    n_types = len(CELL_ORDER)
    C = np.zeros((n_types, n_types), dtype=np.float64)

    for i, target_type in enumerate(CELL_ORDER):
        target_mask = (net.types == target_type)
        if not np.any(target_mask):
            continue
        total_target_input = np.sum(W[target_mask, :])
        if total_target_input <= 1e-12:
            continue

        for j, source_type in enumerate(CELL_ORDER):
            source_mask = (net.types == source_type)
            if not np.any(source_mask):
                continue
            sub_w = W[np.ix_(target_mask, source_mask)]
            C[i, j] = np.sum(sub_w) / total_target_input

    return C, CELL_ORDER


def plot_panel_2a_spatial_transcriptomics(
    net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 2A: Spatial transcriptomics transverse mapping of 9 cardinal cell types
    across the lumbar spinal cord with Rexed laminae annotations.
    """
    fig, ax = plt.subplots(figsize=(6.5, 6.0), dpi=dpi)

    ax.axvline(0, color='#888888', linestyle='--', lw=1.2, alpha=0.7, label='Midline')
    ax.add_patch(patches.Ellipse((0, 800), 2800, 1400, fill=False, edgecolor='#aaaaaa', lw=1.5, linestyle=':'))
    ax.add_patch(patches.Ellipse((0, 450), 2200, 700, fill=False, edgecolor='#cccccc', lw=1.0, linestyle=':'))

    for c_type in CELL_ORDER:
        mask = (net.types == c_type)
        if np.any(mask):
            ax.scatter(
                net.pos_x[mask],
                net.pos_y[mask],
                c=CELL_COLORS.get(c_type, '#333333'),
                s=18,
                alpha=0.85,
                edgecolor='none',
                label=f"{c_type} (n={np.sum(mask)})"
            )

    ax.set_title('2A: Spatial Transcriptomics & Laminar Mapping', fontsize=11, fontweight='bold', pad=8)
    ax.set_xlabel('Mediolateral $X$ (µm)', fontsize=9.5, fontweight='bold')
    ax.set_ylabel('Dorsoventral $Y$ (µm)', fontsize=9.5, fontweight='bold')
    ax.set_xlim(-1750, 1750)
    ax.set_ylim(0, 1650)
    ax.grid(True, linestyle=':', alpha=0.35)
    ax.legend(loc='upper right', fontsize=7.5, frameon=True, ncol=2)

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_2b_segmental_abundance(
    net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 2B: Segmental distribution and cell-type abundance across T13-S4.
    """
    fig, ax = plt.subplots(figsize=(7.0, 4.5), dpi=dpi)

    segments = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4']
    neuron_segs = get_neuron_segments(net)
    seg_counts = {c: np.zeros(len(segments)) for c in CELL_ORDER}

    for s_idx, seg in enumerate(segments):
        s_mask = (neuron_segs == seg)
        for c_type in CELL_ORDER:
            c_mask = (net.types == c_type)
            seg_counts[c_type][s_idx] = np.sum(s_mask & c_mask)

    bottom = np.zeros(len(segments))
    for c_type in CELL_ORDER:
        counts = seg_counts[c_type]
        ax.bar(segments, counts, bottom=bottom, color=CELL_COLORS[c_type], label=c_type, edgecolor='black', lw=0.3, width=0.65)
        bottom += counts

    ax.set_title('2B: Segmental Abundance Across Lumbo-Sacral Cord ($T_{13} \\rightarrow S_4$)', fontsize=11, fontweight='bold', pad=8)
    ax.set_xlabel('Spinal Segment', fontsize=9.5, fontweight='bold')
    ax.set_ylabel('Neuron Count', fontsize=9.5, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.35, axis='y')
    ax.legend(loc='upper right', fontsize=7.5, frameon=True, ncol=3)

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_2c_directional_kernels(
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 2C: 3D Directional Projection Kernels along Rostrocaudal (RC),
    Mediolateral (ML), and Dorsoventral (DV) axes for the 9 cardinal cell types.
    """
    fig, (ax_rc, ax_ml, ax_dv) = plt.subplots(1, 3, figsize=(14.0, 4.2), dpi=dpi)

    dz = np.linspace(-4000, 4000, 400)
    dx = np.linspace(-1500, 1500, 300)
    dy = np.linspace(-1000, 1000, 300)
    pw = 500.0

    kernel_params = {
        'V2a-2': (7000.0, 'bi', 1.0),
        'V2a-1': (500.0, 'cau', 1.0),
        'V1':    (2000.0, 'ro', -1.0),
        'V2b':   (4000.0, 'cau', -1.0),
        'V0v':   (3400.0, 'ro', 1.0),
        'V0d':   (500.0, 'loc', -1.0),
        'V3':    (500.0, 'cau', 1.0),
        'dI6':   (5000.0, 'cau', -1.0),
        'MN':    (300.0, 'loc', 1.0)
    }

    # 1. Rostrocaudal (RC)
    for c_type, (mu, mode, sign) in kernel_params.items():
        if mode == 'cau':
            k_rc = np.exp(-((dz - mu)**2) / (2.0 * pw**2))
        elif mode == 'ro':
            k_rc = np.exp(-((dz + mu)**2) / (2.0 * pw**2))
        elif mode == 'bi':
            k_rc = np.exp(-((np.abs(dz) - mu)**2) / (2.0 * pw**2))
        else: # loc
            k_rc = np.exp(-(dz**2) / (2.0 * (mu + 1e-6)**2))

        ax_rc.plot(dz, sign * k_rc, color=CELL_COLORS[c_type], lw=1.8, label=f"{c_type} ({mode}, $\\mu={int(mu)}$µm)")

    ax_rc.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax_rc.axvline(0, color='gray', linestyle=':', lw=1.0)
    ax_rc.set_title('2C: Rostrocaudal Projections (RC, $\\Delta Z$)', fontsize=10.5, fontweight='bold', pad=8)
    ax_rc.set_xlabel('Rostrocaudal Distance $\\Delta Z$ (µm)', fontsize=9, fontweight='bold')
    ax_rc.set_ylabel('Directional Kernel ($P_{\\text{syn}}$)', fontsize=9, fontweight='bold')
    ax_rc.grid(True, linestyle=':', alpha=0.35)
    ax_rc.legend(loc='upper right', fontsize=6.5, frameon=True)

    # 2. Mediolateral (ML)
    for c_type, (_, _, sign) in kernel_params.items():
        k_ml = np.exp(-(dx**2) / (2.0 * (pw if c_type in ['V2a-2', 'V2b', 'V3'] else pw/2.0)**2))
        ax_ml.plot(dx, sign * k_ml, color=CELL_COLORS[c_type], lw=1.8)

    ax_ml.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax_ml.axvline(0, color='gray', linestyle=':', lw=1.0)
    ax_ml.set_title('Mediolateral Projections (ML, $\\Delta X$)', fontsize=10.5, fontweight='bold', pad=8)
    ax_ml.set_xlabel('Mediolateral Distance $\\Delta X$ (µm)', fontsize=9, fontweight='bold')
    ax_ml.grid(True, linestyle=':', alpha=0.35)

    # 3. Dorsoventral (DV)
    for c_type, (_, _, sign) in kernel_params.items():
        k_dv = np.exp(-(dy**2) / (2.0 * pw**2))
        ax_dv.plot(dy, sign * k_dv, color=CELL_COLORS[c_type], lw=1.8)

    ax_dv.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax_dv.axvline(0, color='gray', linestyle=':', lw=1.0)
    ax_dv.set_title('Dorsoventral Projections (DV, $\\Delta Y$)', fontsize=10.5, fontweight='bold', pad=8)
    ax_dv.set_xlabel('Dorsoventral Distance $\\Delta Y$ (µm)', fontsize=9, fontweight='bold')
    ax_dv.grid(True, linestyle=':', alpha=0.35)

    plt.suptitle('Figure 2C: 3D Anisotropic Gaussian Projection Kernels Across RC, ML, and DV Axes', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def get_motor_pool_segment_distribution(data_loader: Any) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    Extracts the average motoneuron distribution per segment (L1-L6) for hindlimb muscle pools
    from MotorneuronsDistribution.xlsx.
    """
    df = data_loader.load_motoneuron_distribution()
    segments = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']
    
    current_muscle = None
    muscle_data = {}
    for i in range(1, len(df)):
        row = df.iloc[i]
        m_name = row['Injected muscle']
        if pd.notna(m_name) and isinstance(m_name, str) and len(m_name.strip()) > 0:
            current_muscle = m_name.strip()
            if current_muscle not in muscle_data:
                muscle_data[current_muscle] = []
        
        vals = row.values[3:9] # segments L1 to L6
        if current_muscle and any(pd.notna(v) for v in vals):
            v_num = [float(v) if pd.notna(v) and str(v).replace('.', '', 1).isdigit() else 0.0 for v in vals]
            if np.sum(v_num) > 0:
                muscle_data[current_muscle].append(v_num)
                
    rep_muscles = ['Iliopsoas', 'Quadriceps', 'Tibialis Anterior', 'Extensor digitorum', 'Soleus', 'Biceps femoris']
    rep_labels = [m for m in rep_muscles if m in muscle_data]
    mat = np.zeros((len(rep_labels), len(segments)))
    for idx, m in enumerate(rep_labels):
        if len(muscle_data[m]) > 0:
            mat[idx, :] = np.mean(muscle_data[m], axis=0)
            
    return mat, rep_labels, segments


def plot_panel_2d_motoneuron_topography(
    data_loader: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 2D: Hindlimb Motoneuron Pool Topography across segments L1-L6
    segregating rostral flexors (Iliopsoas, TA, EDL) and caudal extensors (Quadriceps, Soleus, BF).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5), dpi=dpi, gridspec_kw={'width_ratios': [1.2, 1]})

    mat_dist, rep_labels, segments = get_motor_pool_segment_distribution(data_loader)

    # 1. Heatmap
    im = ax1.imshow(mat_dist, aspect='auto', cmap='magma', origin='upper')
    ax1.set_xticks(np.arange(len(segments)))
    ax1.set_xticklabels(segments, fontsize=9, fontweight='bold')
    ax1.set_yticks(np.arange(len(rep_labels)))
    ax1.set_yticklabels(rep_labels, fontsize=9, fontweight='bold')
    ax1.set_title('2D: Hindlimb Motor Pool Segmental Localization', fontsize=10.5, fontweight='bold', pad=8)
    ax1.set_xlabel('Spinal Segment', fontsize=9, fontweight='bold')
    ax1.set_ylabel('Muscle Motor Pool', fontsize=9, fontweight='bold')
    plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04, label='Mean Labeled MNs')

    # 2. Rostrocaudal Density: Flexor vs Extensor
    flex_idx = [i for i, m in enumerate(rep_labels) if m in ['Iliopsoas', 'Tibialis Anterior', 'Extensor digitorum']]
    ext_idx = [i for i, m in enumerate(rep_labels) if m in ['Quadriceps', 'Soleus', 'Biceps femoris']]

    flex_profile = np.sum(mat_dist[flex_idx, :], axis=0) if len(flex_idx) > 0 else mat_dist[0, :]
    ext_profile = np.sum(mat_dist[ext_idx, :], axis=0) if len(ext_idx) > 0 else mat_dist[-1, :]

    ax2.plot(segments, flex_profile, color='#1f77b4', marker='o', lw=2.2, label='Flexor Pools (e.g. IP, TA, EDL)')
    ax2.plot(segments, ext_profile, color='#d62728', marker='s', lw=2.2, label='Extensor Pools (e.g. Quad, Sol, BF)')
    ax2.set_title('Rostral Flexor vs Caudal Extensor Segregation', fontsize=10.5, fontweight='bold', pad=8)
    ax2.set_xlabel('Spinal Segment', fontsize=9, fontweight='bold')
    ax2.set_ylabel('Total Labeled Motoneurons', fontsize=9, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.35)
    ax2.legend(loc='upper right', fontsize=8, frameon=True)

    plt.suptitle('Figure 2D: Motoneuron Pool Topography Across Lumbo-Sacral Spinal Enlargement', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_2e_pairwise_connectivity(
    net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 2E: Full N x N Pairwise Connectivity Matrix and Ipsilateral / Contralateral submatrices.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14.0, 4.2), dpi=dpi)

    W = net.conn_mat
    vmax = np.percentile(np.abs(W[W != 0]), 99) if np.any(W != 0) else 1.0

    # 1. Full Matrix
    im1 = ax1.imshow(W, cmap='bwr', aspect='auto', vmin=-vmax, vmax=vmax)
    ax1.set_title(f'2E: Full Connectome ($N={net.n_neurons}$)', fontsize=10.5, fontweight='bold', pad=8)
    ax1.set_xlabel('Presynaptic Index ($j$)', fontsize=9, fontweight='bold')
    ax1.set_ylabel('Postsynaptic Index ($i$)', fontsize=9, fontweight='bold')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04, label='Weight ($W_{ij}$)')

    # 2. Ipsilateral Submatrix
    ipsi_mask = (np.outer(net.latera, net.latera) > 0)
    W_ipsi = np.where(ipsi_mask, W, 0.0)
    im2 = ax2.imshow(W_ipsi, cmap='bwr', aspect='auto', vmin=-vmax, vmax=vmax)
    ax2.set_title(f'Ipsilateral Submatrix ({np.count_nonzero(W_ipsi):,} syn)', fontsize=10.5, fontweight='bold', pad=8)
    ax2.set_xlabel('Presynaptic Index ($j$)', fontsize=9, fontweight='bold')
    ax2.set_ylabel('Postsynaptic Index ($i$)', fontsize=9, fontweight='bold')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    # 3. Contralateral Submatrix
    contra_mask = (np.outer(net.latera, net.latera) < 0)
    W_contra = np.where(contra_mask, W, 0.0)
    im3 = ax3.imshow(W_contra, cmap='bwr', aspect='auto', vmin=-vmax, vmax=vmax)
    ax3.set_title(f'Contralateral Submatrix ({np.count_nonzero(W_contra):,} syn)', fontsize=10.5, fontweight='bold', pad=8)
    ax3.set_xlabel('Presynaptic Index ($j$)', fontsize=9, fontweight='bold')
    ax3.set_ylabel('Postsynaptic Index ($i$)', fontsize=9, fontweight='bold')
    plt.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)

    plt.suptitle('Figure 2E: Macroscopic $N \\times N$ Synaptic Connectivity Matrix & Midline Decomposition', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_2f_cell_type_matrix(
    net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 2F: Normalized (9 x 9) Cell Type-to-Cell Type interaction matrix C_ij.
    """
    fig, ax = plt.subplots(figsize=(6.5, 5.8), dpi=dpi)

    C, type_labels = compute_cell_type_connectivity_matrix(net)

    im = ax.imshow(C * 100.0, cmap='Blues', aspect='auto', origin='upper')
    ax.set_xticks(np.arange(len(type_labels)))
    ax.set_xticklabels(type_labels, rotation=45, ha='right', fontsize=9, fontweight='bold')
    ax.set_yticks(np.arange(len(type_labels)))
    ax.set_yticklabels(type_labels, fontsize=9, fontweight='bold')

    for i, t in enumerate(type_labels):
        ax.get_xticklabels()[i].set_color(CELL_COLORS[t])
        ax.get_yticklabels()[i].set_color(CELL_COLORS[t])

    for i in range(len(type_labels)):
        for j in range(len(type_labels)):
            val = C[i, j] * 100.0
            col = 'white' if val > 20.0 else 'black'
            ax.text(j, i, f"{val:.1f}%", ha='center', va='center', color=col, fontsize=7.5, fontweight='bold')

    ax.set_title('2F: Cell Type–to–Cell Type Interaction Matrix ($C_{ij}$)', fontsize=11, fontweight='bold', pad=8)
    ax.set_xlabel('Presynaptic Source Type ($j$)', fontsize=9.5, fontweight='bold')
    ax.set_ylabel('Postsynaptic Target Type ($i$)', fontsize=9.5, fontweight='bold')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='Input Share (%)')

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def plot_panel_2g_net_projectome(
    net: Any,
    output_path: Optional[str] = None,
    dpi: int = 300
) -> plt.Figure:
    """
    Panel 2G: Net Lumbar Spinal Projectome: 1D projection profiles along the
    rostrocaudal axis showing the emergent asymmetric Mexican hat (Ipsilateral)
    and commissural profiles (Contralateral).
    """
    from figure5_analysis import compute_projectome_1d_profile

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5), dpi=dpi)

    dz_ipsi, prof_ipsi = compute_projectome_1d_profile(net, ipsilateral_only=True, max_dist_um=4500.0)
    dz_contra, prof_contra = compute_projectome_1d_profile(net, contralateral_only=True, max_dist_um=4500.0)

    # 1. Ipsilateral Projectome (Mexican Hat)
    ax1.plot(dz_ipsi, prof_ipsi, color='#111111', lw=2.4, label='Net Ipsilateral Projectome')
    ax1.fill_between(dz_ipsi, 0, np.clip(prof_ipsi, 0, None), color='#e41a1c', alpha=0.35, label='Local Excitation')
    ax1.fill_between(dz_ipsi, 0, np.clip(prof_ipsi, None, 0), color='#377eb8', alpha=0.35, label='Surround Inhibition')
    ax1.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax1.axvline(0, color='gray', linestyle=':', lw=1.0)
    ax1.set_title('2G: Net Ipsilateral Projectome (Asymmetric Mexican Hat)', fontsize=10.5, fontweight='bold', pad=8)
    ax1.set_xlabel('Rostrocaudal Distance $\\Delta Z$ (µm)', fontsize=9, fontweight='bold')
    ax1.set_ylabel('Synaptic Density (Total Weight)', fontsize=9, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.35)
    ax1.legend(loc='upper right', fontsize=8, frameon=True)

    # 2. Contralateral Projectome (Commissural)
    ax2.plot(dz_contra, prof_contra, color='#9467bd', lw=2.4, label='Net Contralateral Projectome')
    ax2.fill_between(dz_contra, 0, np.clip(prof_contra, 0, None), color='#ff7f0e', alpha=0.35, label='Commissural Excitation (V0v, V3)')
    ax2.fill_between(dz_contra, 0, np.clip(prof_contra, None, 0), color='#984ea3', alpha=0.35, label='Commissural Inhibition (V0d, dI6)')
    ax2.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax2.axvline(0, color='gray', linestyle=':', lw=1.0)
    ax2.set_title('Net Contralateral Commissural Projectome', fontsize=10.5, fontweight='bold', pad=8)
    ax2.set_xlabel('Rostrocaudal Distance $\\Delta Z$ (µm)', fontsize=9, fontweight='bold')
    ax2.set_ylabel('Synaptic Density (Total Weight)', fontsize=9, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.35)
    ax2.legend(loc='upper right', fontsize=8, frameon=True)

    plt.suptitle('Figure 2G: Net Macroscopic Spinal Projectomes Along the Longitudinal Axis', fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
    return fig


def generate_figure2_complete(
    net: Any,
    data_loader: Any,
    output_path: str = "plots/figure2_complete.png",
    dpi: int = 300
) -> plt.Figure:
    """
    Generates unified composite Figure 2 matching Nature Communications layout:
      Top Row: 2A (Spatial Transcriptomics), 2B (Segmental Abundance), 2C (Directional Kernels).
      Bottom Row: 2D (Motoneuron Topography), 2E (Connectivity Matrix), 2F (Cell-to-Cell Matrix C_ij), 2G (Net Mexican Hat).
    """
    from figure5_analysis import compute_projectome_1d_profile

    fig = plt.figure(figsize=(19, 12), dpi=dpi)
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1])

    # 2A: Spatial Transcriptomics (Top Left)
    ax_a = fig.add_subplot(gs[0, 0])
    for c_type in CELL_ORDER:
        mask = (net.types == c_type)
        if np.any(mask):
            ax_a.scatter(net.pos_x[mask], net.pos_y[mask], c=CELL_COLORS.get(c_type, '#333333'), s=10, alpha=0.8)
    ax_a.set_title('A: Spatial Transcriptomics', fontweight='bold', fontsize=10.5)
    ax_a.set_xlabel('Mediolateral $X$ (µm)', fontsize=8.5)
    ax_a.set_ylabel('Dorsoventral $Y$ (µm)', fontsize=8.5)
    ax_a.grid(True, linestyle=':', alpha=0.3)

    # 2B: Segmental Abundance (Top Middle-Left)
    ax_b = fig.add_subplot(gs[0, 1])
    segments = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4']
    neuron_segs = get_neuron_segments(net)
    bottom = np.zeros(len(segments))
    for c_type in CELL_ORDER:
        counts = [np.sum((neuron_segs == s) & (net.types == c_type)) for s in segments]
        ax_b.bar(segments, counts, bottom=bottom, color=CELL_COLORS[c_type], edgecolor='black', lw=0.2, width=0.65)
        bottom += counts
    ax_b.set_title('B: Segmental Abundance', fontweight='bold', fontsize=10.5)
    ax_b.set_xlabel('Segment', fontsize=8.5)
    ax_b.set_ylabel('Neuron Count', fontsize=8.5)

    # 2C: 3D Directional Kernels (Top Right 2 columns)
    ax_c = fig.add_subplot(gs[0, 2:])
    dz = np.linspace(-4000, 4000, 300)
    pw = 500.0
    kernel_params = {
        'V2a-2': (7000.0, 'bi', 1.0),
        'V2a-1': (500.0, 'cau', 1.0),
        'V1':    (2000.0, 'ro', -1.0),
        'V2b':   (4000.0, 'cau', -1.0),
        'V0v':   (3400.0, 'ro', 1.0),
        'V0d':   (500.0, 'loc', -1.0),
        'V3':    (500.0, 'cau', 1.0),
        'dI6':   (5000.0, 'cau', -1.0),
        'MN':    (300.0, 'loc', 1.0)
    }
    for c_type, (mu, mode, sign) in kernel_params.items():
        if mode == 'cau':
            k_rc = np.exp(-((dz - mu)**2) / (2.0 * pw**2))
        elif mode == 'ro':
            k_rc = np.exp(-((dz + mu)**2) / (2.0 * pw**2))
        elif mode == 'bi':
            k_rc = np.exp(-((np.abs(dz) - mu)**2) / (2.0 * pw**2))
        else:
            k_rc = np.exp(-(dz**2) / (2.0 * (mu + 1e-6)**2))
        ax_c.plot(dz, sign * k_rc, color=CELL_COLORS[c_type], lw=1.8, label=c_type)
    ax_c.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax_c.set_title('C: Rostrocaudal Projection Kernels ($P_{\\text{syn}}$)', fontweight='bold', fontsize=10.5)
    ax_c.set_xlabel('Distance $\\Delta Z$ (µm)', fontsize=8.5)
    ax_c.legend(loc='upper right', fontsize=7, ncol=3, frameon=True)
    ax_c.grid(True, linestyle=':', alpha=0.3)

    # 2D: Motoneuron Pool Topography (Bottom Col 0)
    ax_d = fig.add_subplot(gs[1, 0])
    mat_dist, rep_labels, seg_mn = get_motor_pool_segment_distribution(data_loader)
    im_d = ax_d.imshow(mat_dist, aspect='auto', cmap='magma', origin='upper')
    ax_d.set_xticks(np.arange(len(seg_mn)))
    ax_d.set_xticklabels(seg_mn, fontsize=8.0, fontweight='bold')
    ax_d.set_yticks(np.arange(len(rep_labels)))
    ax_d.set_yticklabels(rep_labels, fontsize=8.0)
    ax_d.set_title('D: Motor Pool Topography', fontweight='bold', fontsize=10.5)
    plt.colorbar(im_d, ax=ax_d, fraction=0.046, pad=0.04)

    # 2E: Full Matrix W (Bottom Col 1)
    ax_e = fig.add_subplot(gs[1, 1])
    W = net.conn_mat
    vmax = np.percentile(np.abs(W[W != 0]), 99) if np.any(W != 0) else 1.0
    im_e = ax_e.imshow(W, cmap='bwr', aspect='auto', vmin=-vmax, vmax=vmax)
    ax_e.set_title('E: $N \\times N$ Connectome ($W$)', fontweight='bold', fontsize=10.5)
    ax_e.set_xlabel('Presynaptic ($j$)', fontsize=8.5)
    ax_e.set_ylabel('Postsynaptic ($i$)', fontsize=8.5)
    plt.colorbar(im_e, ax=ax_e, fraction=0.046, pad=0.04)

    # 2F: Cell Type Interaction Matrix C_ij (Bottom Col 2)
    ax_f = fig.add_subplot(gs[1, 2])
    C, type_labels = compute_cell_type_connectivity_matrix(net)
    im_f = ax_f.imshow(C * 100.0, cmap='Blues', aspect='auto', origin='upper')
    ax_f.set_xticks(np.arange(len(type_labels)))
    ax_f.set_xticklabels(type_labels, rotation=45, fontsize=7.5)
    ax_f.set_yticks(np.arange(len(type_labels)))
    ax_f.set_yticklabels(type_labels, fontsize=7.5)
    ax_f.set_title('F: Cell-to-Cell Matrix ($C_{ij}$)', fontweight='bold', fontsize=10.5)
    plt.colorbar(im_f, ax=ax_f, fraction=0.046, pad=0.04)

    # 2G: Net Projectome (Bottom Col 3)
    ax_g = fig.add_subplot(gs[1, 3])
    dz_ipsi, prof_ipsi = compute_projectome_1d_profile(net, ipsilateral_only=True, max_dist_um=4500.0)
    ax_g.plot(dz_ipsi, prof_ipsi, color='#111111', lw=2.0, label='Ipsi Projectome')
    ax_g.fill_between(dz_ipsi, 0, np.clip(prof_ipsi, 0, None), color='#e41a1c', alpha=0.35)
    ax_g.fill_between(dz_ipsi, 0, np.clip(prof_ipsi, None, 0), color='#377eb8', alpha=0.35)
    ax_g.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax_g.set_title('G: Net Lumbar Projectome', fontweight='bold', fontsize=10.5)
    ax_g.set_xlabel('$\\Delta Z$ (µm)', fontsize=8.5)
    ax_g.grid(True, linestyle=':', alpha=0.3)

    fig.suptitle('Figure 2: Spatial Transcriptomics, 3D Directional Kernels, Motor Pools & Net Lumbar Projectome (Komi et al. 2026)', fontsize=13, fontweight='bold', y=0.99)
    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
        alt_path = os.path.join(os.path.dirname(output_path), "00_figure2_complete.png")
        fig.savefig(alt_path, bbox_inches='tight', dpi=dpi)

    return fig
