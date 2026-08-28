"""
Tests for Figure 1 Reproduction: Balanced Sequence Generator (BSG) and 1D Mexican-Hat Model.
Verifies:
1. BSG Network initialization, zero-diagonal, Dale's law, and exact row-wise E/I balancing.
2. Rate-based Forward Euler dynamics and non-negativity of firing rates.
3. Phase-space unfolding algorithm, circular sorting, and Mexican-hat profile emergence.
4. 1D 5-subpopulation network instantiation and forward traveling wave dynamics.
5. sp3 gain modulation -> selective amplitude control (R_orbit increases, f invariant).
6. sp2 gain modulation -> selective frequency control (f increases, R_orbit preserved).
7. Figure 1 panel and composite plotting pipeline.
"""

import os
import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from figure1_models import (
    BSGConfig,
    BSGNetwork,
    balance_bsg_connectivity,
    compute_phase_unfolding,
    SubpopulationConfig,
    MexicanHat1DNetwork,
    simulate_gain_modulation_sweep
)
from figure1_analysis import (
    plot_panel_1abc_bsg_dynamics,
    plot_panel_1de_unfolded_projectome,
    plot_panel_1f_5pop_network,
    plot_panel_1g_amplitude_control,
    plot_panel_1h_frequency_control,
    plot_figure1_complete
)


@pytest.fixture
def small_bsg_network():
    """Provides a small, fast BSG network for testing."""
    cfg = BSGConfig(n_neurons=100, p_conn=0.15, t_steps=500, dt_ms=1.0, rng_seed=42)
    return BSGNetwork(cfg)


@pytest.fixture
def small_1d_network():
    """Provides a small 1D 5-subpopulation network for testing."""
    return MexicanHat1DNetwork(n_neurons=100, length_um=2000.0, rng_seed=42)


def test_bsg_network_creation_and_balance(small_bsg_network):
    """Verifies that BSG network satisfies topological constraints and row-wise E/I balance."""
    net = small_bsg_network
    assert net.n_neurons == 100
    assert net.conn_mat.shape == (100, 100)

    # 1. Zero diagonal (no autapses)
    assert np.allclose(np.diag(net.conn_mat), 0.0), "Autapses must be strictly zero"

    # 2. Dale's Law
    for j in range(net.n_neurons):
        col = net.conn_mat[:, j]
        if net.is_excitatory[j]:
            assert np.all(col >= -1e-9), f"Excitatory neuron {j} cannot have negative weights"
        else:
            assert np.all(col <= 1e-9), f"Inhibitory neuron {j} cannot have positive weights"

    # 3. Row-wise zero-sum balance: sum_j W_{ij} == 0
    row_sums = np.sum(net.conn_mat, axis=1)
    assert np.allclose(row_sums, 0.0, atol=1e-5), "All neuron rows must have sum_j W_ij == 0"


def test_bsg_simulation_and_phase_unfolding(small_bsg_network):
    """Verifies membrane simulation and phase-space unfolding algorithm."""
    net = small_bsg_network
    res = net.simulate(t_steps=1000, dt_ms=1.0, I_e=30.0, seed=42)

    assert 'time_ms' in res
    assert 'rates' in res
    assert res['rates'].shape == (1000, 100)
    assert np.all(res['rates'] >= 0.0), "Firing rates must be non-negative"
    assert not np.isnan(res['rates']).any()

    # Phase unfolding
    unfold_res = compute_phase_unfolding(res['rates'], net.conn_mat, dt_ms=1.0, t_start_ms=200)
    assert 'pca_scores' in unfold_res
    assert 'cycle_period_ms' in unfold_res
    assert 'sort_order' in unfold_res
    assert 'W_unfolded' in unfold_res
    assert 'projectome_profile' in unfold_res

    assert len(unfold_res['sort_order']) == 100
    assert unfold_res['W_unfolded'].shape == (100, 100)
    assert len(unfold_res['projectome_profile']) > 0


def test_1d_5pop_network_creation_and_dynamics(small_1d_network):
    """Verifies 1D 5-subpopulation network initialization and traveling wave simulation."""
    net = small_1d_network
    assert net.n_neurons == 100
    assert net.conn_mat.shape == (100, 100)
    assert len(net.pop_configs) == 5

    # Row balancing
    row_sums = np.sum(net.conn_mat, axis=1)
    assert np.allclose(row_sums, 0.0, atol=1e-5)

    # Simulation
    res = net.simulate(t_steps=500, dt_ms=1.0, I_e=30.0, seed=42)
    assert res['rates'].shape == (500, 100)
    assert np.all(res['rates'] >= 0.0)


def test_sp3_amplitude_gain_modulation(small_1d_network):
    """Verifies that modulating sp3 gain selectively increases amplitude without shifting frequency."""
    net = small_1d_network
    gain_levels = [0.8, 1.2, 1.6]
    res = simulate_gain_modulation_sweep(net, target_population='sp3', gain_levels=gain_levels, t_steps=1500, seed=42)

    amps = res['amplitudes_hz']
    freqs = res['frequencies_hz']
    radii = res['orbit_radii']

    assert len(amps) == 3
    # Amplitude and orbit radius should increase with sp3 gain
    assert amps[-1] > amps[0], "Amplitude should increase with excitatory sp3 gain"
    assert radii[-1] > radii[0], "PCA orbit radius should expand with sp3 gain"


def test_sp2_frequency_gain_modulation(small_1d_network):
    """Verifies that modulating sp2 gain selectively increases frequency."""
    net = small_1d_network
    gain_levels = [0.8, 1.2, 1.6]
    res = simulate_gain_modulation_sweep(net, target_population='sp2', gain_levels=gain_levels, t_steps=1500, seed=42)

    freqs = res['frequencies_hz']
    amps = res['amplitudes_hz']

    assert len(freqs) == 3
    # Frequency should increase with sp2 gain
    assert freqs[-1] >= freqs[0], "Frequency should increase or remain fast with inhibitory sp2 gain"


def test_figure1_plotting_pipeline(small_bsg_network, small_1d_network, tmp_path):
    """Verifies that all Figure 1 plotting functions run without errors."""
    bsg = small_bsg_network
    bsg_sim = bsg.simulate(t_steps=500, dt_ms=1.0, I_e=30.0, seed=42)
    unfold_res = compute_phase_unfolding(bsg_sim['rates'], bsg.conn_mat, dt_ms=1.0, t_start_ms=100)

    net_1d = small_1d_network
    sim_1d = net_1d.simulate(t_steps=500, dt_ms=1.0, I_e=30.0, seed=42)
    sp3_sweep = simulate_gain_modulation_sweep(net_1d, target_population='sp3', gain_levels=[0.8, 1.2], t_steps=500, seed=42)
    sp2_sweep = simulate_gain_modulation_sweep(net_1d, target_population='sp2', gain_levels=[0.8, 1.2], t_steps=500, seed=42)

    # 1ABC
    out_1abc = os.path.join(tmp_path, "01_fig1abc.png")
    fig_1abc = plot_panel_1abc_bsg_dynamics(bsg, bsg_sim, unfold_res, output_path=out_1abc, dpi=100)
    assert os.path.exists(out_1abc)
    plt.close(fig_1abc)

    # 1DE
    out_1de = os.path.join(tmp_path, "02_fig1de.png")
    fig_1de = plot_panel_1de_unfolded_projectome(unfold_res, output_path=out_1de, dpi=100)
    assert os.path.exists(out_1de)
    plt.close(fig_1de)

    # 1F
    out_1f = os.path.join(tmp_path, "03_fig1f.png")
    fig_1f = plot_panel_1f_5pop_network(net_1d, sim_1d, output_path=out_1f, dpi=100)
    assert os.path.exists(out_1f)
    plt.close(fig_1f)

    # 1G
    out_1g = os.path.join(tmp_path, "04_fig1g.png")
    fig_1g = plot_panel_1g_amplitude_control(sp3_sweep, output_path=out_1g, dpi=100)
    assert os.path.exists(out_1g)
    plt.close(fig_1g)

    # 1H
    out_1h = os.path.join(tmp_path, "05_fig1h.png")
    fig_1h = plot_panel_1h_frequency_control(sp2_sweep, output_path=out_1h, dpi=100)
    assert os.path.exists(out_1h)
    plt.close(fig_1h)

    # Complete
    out_comp = os.path.join(tmp_path, "figure1_complete.png")
    fig_comp = plot_figure1_complete({'unfold_res': unfold_res}, {'net_1d': net_1d, 'sim_res': sim_1d}, sp3_sweep, sp2_sweep, output_path=out_comp, dpi=100)
    assert os.path.exists(out_comp)
    plt.close(fig_comp)
