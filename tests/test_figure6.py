"""
Unit tests for Figure 6 Reproduction:
Spinal Cord Lesion, Targeted Axonal Regrowth, and High-Density Electrophysiology.
"""

import os
import pytest
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from network import Network
from perturbations import (
    create_transverse_lesion,
    regrow_population_connections,
    simulate_lesion_and_regrowth_suite
)
from electrophysiology import (
    VirtualProbe,
    ProbeConfig,
    generate_poisson_spikes,
    estimate_instantaneous_rates,
    compute_channel_phase_lags
)
from figure6_analysis import (
    plot_panel_6a_lesion_projectome,
    plot_panel_6b_post_lesion_dynamics,
    plot_panel_6c_regrowth_comparison,
    plot_panel_6d_functional_recovery,
    plot_panel_6e_probe_insertion,
    plot_panel_6f_multichannel_spiking,
    generate_figure6_complete
)


@pytest.fixture(scope="module")
def small_test_network():
    """Builds a test network with density = 0.5 for fast automated test execution."""
    segments = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4']
    net = Network(
        segments=segments,
        density=0.5,
        symmetry=True,
        balance=True,
        rescale=True,
        rng_seed=42,
        compute_eigenspectrum=False
    )
    return net



def test_create_transverse_lesion(small_test_network):
    """Verifies that transverse lesion severes cross-boundary connections."""
    net = small_test_network
    z_lesion = 4000.0
    lesioned_net = create_transverse_lesion(net, z_pos_um=z_lesion)

    assert hasattr(lesioned_net, 'lesion_mask')
    assert hasattr(lesioned_net, 'n_lesioned_synapses')
    assert lesioned_net.n_lesioned_synapses > 0

    # Verify that all connections crossing z_lesion are now 0.0
    source = (net.pos_z < z_lesion)
    target = (net.pos_z > z_lesion)
    crossing = (source[:, None] & target[None, :]) | (target[:, None] & source[None, :])

    assert np.all(lesioned_net.conn_mat[crossing] == 0.0)
    assert lesioned_net.sparsity >= net.sparsity


def test_regrow_population_connections(small_test_network):
    """Verifies selective regrowth restores synapses for target cell type."""
    net = small_test_network
    z_lesion = 4000.0
    lesioned_net = create_transverse_lesion(net, z_pos_um=z_lesion)

    target_pop = 'V2a-2'
    regrown_net = regrow_population_connections(lesioned_net, target_population=target_pop)

    assert hasattr(regrown_net, 'regrown_population')
    assert regrown_net.regrown_population == target_pop
    assert hasattr(regrown_net, 'n_restored_synapses')

    # Verify that restored synapses have nonzero weights
    pop_mask = (regrown_net.types == target_pop)
    source = (net.pos_z < z_lesion)
    target = (net.pos_z > z_lesion)
    crossing = (source[:, None] & target[None, :]) | (target[:, None] & source[None, :])
    restored_target = crossing & pop_mask[None, :] & (net.conn_mat != 0.0)

    if np.any(restored_target):
        assert np.all(regrown_net.conn_mat[restored_target] != 0.0)


def test_virtual_probe_insertion_and_sampling(small_test_network):
    """Verifies virtual 32-channel probe geometry and unit sampling."""
    cfg = ProbeConfig(
        n_channels=32,
        pitch_um=50.0,
        detection_radius_um=50.0,
        tip_x_um=0.0,
        tip_y_um=300.0,
        tip_z_um=4000.0
    )
    probe = VirtualProbe(cfg)
    assert probe.channel_positions_um.shape == (32, 3)

    sample_info = probe.sample_network(small_test_network)
    assert 'n_detected_units' in sample_info
    assert 'channel_assignments' in sample_info
    assert len(probe.channel_assignments) == probe.n_detected_units


def test_poisson_spiking_and_rate_smoothing():
    """Verifies Poisson spike train generation and Gaussian smoothing."""
    T, N = 1000, 50
    synthetic_rates = np.abs(np.sin(np.linspace(0, 10 * np.pi, T)))[:, None] * np.ones((1, N)) * 20.0

    spikes = generate_poisson_spikes(synthetic_rates, scale=75.0, seed=42)
    assert spikes.shape == (T, N)
    assert spikes.dtype == bool
    assert np.any(spikes)

    smoothed_rates = estimate_instantaneous_rates(spikes, sigma_ms=50.0, dt_ms=1.0)
    assert smoothed_rates.shape == (T, N)
    assert np.all(smoothed_rates >= 0.0)


def test_channel_phase_lags():
    """Verifies multi-channel traveling wave phase lag computation."""
    T = 1000
    K = 32
    time = np.linspace(0, 1, T)
    # Simulate traveling wave with depth-dependent phase shift
    ch_rates = np.zeros((T, K))
    for k in range(K):
        phase = k * (2.0 * np.pi / K)
        ch_rates[:, k] = 10.0 + 5.0 * np.sin(2.0 * np.pi * 5.0 * time + phase)

    phase_metrics = compute_channel_phase_lags(ch_rates, dt_ms=1.0, t_start_ms=0)
    assert 'phase_lags_rad' in phase_metrics
    assert 'active_channels' in phase_metrics
    assert len(phase_metrics['phase_lags_rad']) == K


def test_figure6_panel_plotting(small_test_network, tmp_path):
    """Verifies that all Figure 6 panel plot generators run without errors."""
    net = small_test_network
    lesioned_net = create_transverse_lesion(net, z_pos_um=4000.0)

    # 6A
    out_6a = os.path.join(tmp_path, "test_6a.png")
    fig_6a = plot_panel_6a_lesion_projectome(net, lesioned_net, output_path=out_6a, dpi=100)
    assert os.path.exists(out_6a)
    plt.close(fig_6a)

    # 6C
    reg_nets = {
        'regrowth_V2a-2': regrow_population_connections(lesioned_net, 'V2a-2'),
        'regrowth_V1': regrow_population_connections(lesioned_net, 'V1')
    }
    out_6c = os.path.join(tmp_path, "test_6c.png")
    fig_6c = plot_panel_6c_regrowth_comparison(net, lesioned_net, reg_nets, output_path=out_6c, dpi=100)
    assert os.path.exists(out_6c)
    plt.close(fig_6c)

    # 6E
    probe = VirtualProbe(ProbeConfig(tip_x_um=0.0, tip_y_um=300.0, tip_z_um=4000.0))
    probe.sample_network(net)
    out_6e = os.path.join(tmp_path, "test_6e.png")
    fig_6e = plot_panel_6e_probe_insertion(net, probe, output_path=out_6e, dpi=100)
    assert os.path.exists(out_6e)
    plt.close(fig_6e)

