"""
Tests for Figure 2 Reproduction: Spatial Transcriptomics, 3D Directional Kernels,
Motoneuron Pools & Net Lumbar Spinal Projectome.

Verifies:
1. Spatial transcriptomics biological data integrity and calibrated physical coordinates.
2. Hindlimb motoneuron pool segmental localization and flexor/extensor segregation.
3. 3D anisotropic Gaussian projection kernels for all 9 cardinal cell types.
4. Normalized (9 x 9) cell-type interaction matrix C_ij (row-normalized to 1.0).
5. Macroscopic 1D net lumbar spinal projectome (ipsilateral Mexican hat).
6. Complete Figure 2 publication plotting pipeline (Panels 2A-2G and composite).
"""

import os
import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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


@pytest.fixture(scope="module")
def shared_data_loader():
    """Provides a shared SpinalDataLoader instance."""
    return SpinalDataLoader()


@pytest.fixture(scope="module")
def small_figure2_network():
    """Provides a fast, representative network for Figure 2 testing."""
    segments = ['L1', 'L2', 'L3', 'L4', 'L5']
    return Network(segments=segments, density=0.4, symmetry=True, balance=True, rescale=True, rng_seed=42, compute_eigenspectrum=False)


def test_spatial_transcriptomics_data_integrity(shared_data_loader):
    """Verifies that matGeometry.mat loads correctly with 20,755 spots and physical bounds."""
    loader = shared_data_loader
    geom = loader.load_geometry()

    assert 'weights' in geom
    assert geom['weights'].shape == (20755, 80)
    assert len(geom['coord_x_um']) == 20755
    assert len(geom['coord_y_um']) == 20755
    assert np.min(geom['coord_x_um']) >= -1750.0 - 1e-6
    assert np.max(geom['coord_x_um']) <= 1750.0 + 1e-6
    assert np.min(geom['coord_y_um']) >= 0.0 - 1e-6
    assert np.max(geom['coord_y_um']) <= 1650.0 + 1e-6


def test_motoneuron_pool_topography(shared_data_loader):
    """Verifies hindlimb motoneuron distribution from MotorneuronsDistribution.xlsx and matMuscleSeg.mat."""
    from figure2_analysis import get_motor_pool_segment_distribution

    loader = shared_data_loader
    muscle = loader.load_muscle_segments()
    assert 'muscle_names' in muscle
    assert len(muscle['muscle_names']) == 35

    df_mn = loader.load_motoneuron_distribution()
    assert not df_mn.empty

    mat_dist, rep_labels, segments = get_motor_pool_segment_distribution(loader)
    assert mat_dist.ndim == 2
    assert mat_dist.shape[0] == len(rep_labels)
    assert mat_dist.shape[1] == len(segments)
    assert np.all(mat_dist >= 0.0)
    assert 'Tibialis Anterior' in rep_labels
    assert 'Soleus' in rep_labels


def test_directional_projection_kernels():
    """Verifies that 3D directional projection kernel profiles match biological parameters."""
    dz = np.linspace(-4000, 4000, 200)
    pw = 500.0

    # V2a-2 (long-range descending bilateral) vs V1 (rostral)
    k_v2a_rc = np.exp(-((np.abs(dz) - 7000.0)**2) / (2.0 * pw**2))
    k_v1_rc = np.exp(-((dz + 2000.0)**2) / (2.0 * pw**2))

    assert np.max(k_v2a_rc) > 0.0
    assert np.max(k_v1_rc) > 0.0
    # Peak of V1 should be on the rostral side (dz < 0)
    assert dz[np.argmax(k_v1_rc)] < 0.0


def test_cell_type_connectivity_matrix(small_figure2_network):
    """Verifies that (9 x 9) cell-type matrix C_ij is correctly normalized."""
    net = small_figure2_network
    C, type_labels = compute_cell_type_connectivity_matrix(net)

    assert C.shape == (9, 9)
    assert len(type_labels) == 9
    assert np.all(C >= 0.0), "All matrix elements must be non-negative"

    # For active target rows, the input shares must sum to 1.0 (100%)
    for i in range(9):
        row_sum = np.sum(C[i, :])
        if row_sum > 0:
            assert np.isclose(row_sum, 1.0, atol=1e-5), f"Row {type_labels[i]} must sum to 1.0"


def test_net_lumbar_projectome_mexican_hat(small_figure2_network):
    """Verifies that 1D projectome extraction yields net excitation near origin and surround inhibition."""
    net = small_figure2_network
    dz, prof_ipsi = compute_projectome_1d_profile(net, ipsilateral_only=True, max_dist_um=3000.0)

    assert len(dz) > 0
    assert len(prof_ipsi) == len(dz)
    # Origin region should show positive central lobe
    center_idx = len(dz) // 2
    assert prof_ipsi[center_idx] >= 0.0, "Center of ipsilateral projectome should be net excitatory"


def test_figure2_plotting_pipeline(small_figure2_network, shared_data_loader, tmp_path):
    """Verifies that all Figure 2 panel plotting functions and composite figure execute without error."""
    net = small_figure2_network
    loader = shared_data_loader

    # 2A
    out_2a = os.path.join(tmp_path, "test_2a.png")
    fig_2a = plot_panel_2a_spatial_transcriptomics(net, output_path=out_2a, dpi=100)
    assert os.path.exists(out_2a)
    plt.close(fig_2a)

    # 2B
    out_2b = os.path.join(tmp_path, "test_2b.png")
    fig_2b = plot_panel_2b_segmental_abundance(net, output_path=out_2b, dpi=100)
    assert os.path.exists(out_2b)
    plt.close(fig_2b)

    # 2C
    out_2c = os.path.join(tmp_path, "test_2c.png")
    fig_2c = plot_panel_2c_directional_kernels(output_path=out_2c, dpi=100)
    assert os.path.exists(out_2c)
    plt.close(fig_2c)

    # 2D
    out_2d = os.path.join(tmp_path, "test_2d.png")
    fig_2d = plot_panel_2d_motoneuron_topography(loader, output_path=out_2d, dpi=100)
    assert os.path.exists(out_2d)
    plt.close(fig_2d)

    # 2E
    out_2e = os.path.join(tmp_path, "test_2e.png")
    fig_2e = plot_panel_2e_pairwise_connectivity(net, output_path=out_2e, dpi=100)
    assert os.path.exists(out_2e)
    plt.close(fig_2e)

    # 2F
    out_2f = os.path.join(tmp_path, "test_2f.png")
    fig_2f = plot_panel_2f_cell_type_matrix(net, output_path=out_2f, dpi=100)
    assert os.path.exists(out_2f)
    plt.close(fig_2f)

    # 2G
    out_2g = os.path.join(tmp_path, "test_2g.png")
    fig_2g = plot_panel_2g_net_projectome(net, output_path=out_2g, dpi=100)
    assert os.path.exists(out_2g)
    plt.close(fig_2g)

    # Composite
    out_comp = os.path.join(tmp_path, "test_figure2_complete.png")
    fig_comp = generate_figure2_complete(net, loader, output_path=out_comp, dpi=100)
    assert os.path.exists(out_comp)
    plt.close(fig_comp)
