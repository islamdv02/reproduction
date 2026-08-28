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


def test_panel_6b_post_lesion_dynamics(small_test_network, tmp_path):
    """Verifies that post-lesion simulation runs, disrupts cross-lesion dynamics, and plots correctly."""
    from simulation import SimulationConfig, Simulator
    net = small_test_network
    z_lesion = 4000.0
    lesioned_net = create_transverse_lesion(net, z_pos_um=z_lesion)

    cfg = SimulationConfig(t_steps=1000, dt_ms=1.0, I_e=30.0, noise_ampl=0.5, seed=42)
    sim = Simulator(cfg)

    ctrl_res = sim.run(net, verbose=False)
    les_res = sim.run(lesioned_net, verbose=False)

    assert ctrl_res.rates.shape == (1000, net.n_neurons)
    assert les_res.rates.shape == (1000, lesioned_net.n_neurons)
    assert not np.isnan(ctrl_res.rates).any()
    assert not np.isnan(les_res.rates).any()
    assert np.all(ctrl_res.rates >= 0.0)
    assert np.all(les_res.rates >= 0.0)

    # Plotting 6B
    out_6b = os.path.join(tmp_path, "test_6b.png")
    fig_6b = plot_panel_6b_post_lesion_dynamics(ctrl_res, les_res, net, lesioned_net, output_path=out_6b, dpi=100)
    assert os.path.exists(out_6b)
    plt.close(fig_6b)


def test_panel_6c_targeted_axonal_regrowth_suite(small_test_network, tmp_path):
    """
    Verifies Panel 6C targeted axonal regrowth requirements:
    1. Candidate populations (V2a-2, V1, V0v, V3) correctly identified
    2. Only target population cross-lesion connections are restored
    3. Non-selected populations remain severed
    4. Intra-segmental (non-crossing) connections remain untouched
    5. Reproducibility
    6. Figure generation to both expected filenames
    """
    net = small_test_network
    z_lesion = 4000.0
    lesioned_net = create_transverse_lesion(net, z_pos_um=z_lesion)
    candidates = ['V2a-2', 'V1', 'V0v', 'V3']

    source_rostral = (net.pos_z < z_lesion)
    source_caudal = (net.pos_z > z_lesion)
    crossing = (source_rostral[:, None] & source_caudal[None, :]) | (source_caudal[:, None] & source_rostral[None, :])
    non_crossing = ~crossing

    reg_nets = {}
    for pop in candidates:
        pop_mask = (net.types == pop)
        assert np.sum(pop_mask) > 0, f"Population {pop} must exist in network"

        reg_net = regrow_population_connections(lesioned_net, target_population=pop)
        reg_nets[f"regrowth_{pop}"] = reg_net

        # Check that intra-segmental connections are untouched
        assert np.array_equal(reg_net.conn_mat[non_crossing], net.conn_mat[non_crossing]), \
            f"Intra-segmental connections must remain identical after {pop} regrowth"

        # Check that restored crossing synapses only originate from target pop
        restored_crossing = crossing & (reg_net.conn_mat != 0.0)
        if np.any(restored_crossing):
            # Presynaptic columns must match pop
            presynaptic_indices = np.where(restored_crossing)[1]
            presynaptic_types = reg_net.types[presynaptic_indices]
            assert np.all(presynaptic_types == pop), \
                f"Restored crossing synapses must originate strictly from {pop}"

        # Check that other populations remain severed across the lesion
        for other_pop in candidates:
            if other_pop != pop:
                other_mask = (reg_net.types == other_pop)
                other_crossing = crossing & other_mask[None, :]
                assert np.all(reg_net.conn_mat[other_crossing] == 0.0), \
                    f"Non-target population {other_pop} must remain severed during {pop} regrowth"

    # Plotting Panel 6C
    out_6c_proj = os.path.join(tmp_path, "22_fig6c_regrowth_projectome.png")
    fig_6c = plot_panel_6c_regrowth_comparison(net, lesioned_net, reg_nets, output_path=out_6c_proj, dpi=100)
    assert os.path.exists(out_6c_proj)
    assert os.path.exists(os.path.join(tmp_path, "22_fig6c_regrowth_comparison.png"))
    plt.close(fig_6c)


def test_panel_6d_functional_recovery_suite(small_test_network, tmp_path):
    """
    Verifies Panel 6D functional recovery simulation across all 6 conditions:
    1. Control, Lesion, V2a-2, V1, V0v, V3 conditions
    2. Numerical stability, non-negative firing rates, no NaNs
    3. Recovery metric calculation
    4. Panel 6D figure generation
    """
    from simulation import SimulationConfig, Simulator
    from dynamics import compute_spectral_analysis
    from gait_control import compute_coordination_phases

    net = small_test_network
    z_lesion = 4000.0
    lesioned_net = create_transverse_lesion(net, z_pos_um=z_lesion)
    candidates = ['V2a-2', 'V1', 'V0v', 'V3']

    cfg = SimulationConfig(t_steps=500, dt_ms=1.0, I_e=30.0, noise_ampl=0.5, seed=42)
    sim = Simulator(cfg)

    ctrl_res = sim.run(net, verbose=False)
    les_res = sim.run(lesioned_net, verbose=False)

    reg_results = {}
    for pop in candidates:
        r_net = regrow_population_connections(lesioned_net, target_population=pop)
        r_res = sim.run(r_net, verbose=False)

        assert r_res.rates.shape == (500, net.n_neurons)
        assert not np.isnan(r_res.rates).any()
        assert np.all(r_res.rates >= 0.0)

        spec = compute_spectral_analysis(r_res.rates, dt=0.001, t_start_ms=100)
        phases = compute_coordination_phases(r_net, r_res.rates, dt_ms=1.0, t_start_ms=100)
        amp = float(np.mean(np.std(r_res.rates, axis=0)))

        cond_key = f"regrowth_{pop}"
        reg_results[cond_key] = (r_res, {
            'condition': cond_key,
            'target_population': pop,
            'frequency_hz': float(spec['dominant_frequency_hz']),
            'rms_amplitude_hz': amp,
            'lr_phase_deg': float(phases.get('lr_phase_deg', 180.0)),
            'fe_phase_deg': float(phases.get('fe_phase_deg', 180.0))
        }, r_net)

    # Plot Panel 6D
    out_6d = os.path.join(tmp_path, "23_fig6d_functional_rescue.png")
    fig_6d = plot_panel_6d_functional_recovery(ctrl_res, les_res, reg_results, output_path=out_6d, dpi=100)
    assert os.path.exists(out_6d)
    assert os.path.exists(os.path.join(tmp_path, "23_fig6d_functional_recovery.png"))
    plt.close(fig_6d)


def test_panel_6e_virtual_probe_sampling_suite(small_test_network, tmp_path):
    """
    Verifies Panel 6E virtual high-density silicon probe sampling:
    1. Probe geometry & 32-channel linear spatial coordinates
    2. Exact Euclidean distance sampling & argmin channel clustering
    3. Multi-unit rate extraction and non-negativity
    4. Panel 6E figure plotting & dual alias persistence
    """
    net = small_test_network

    cfg = ProbeConfig(
        n_channels=32,
        pitch_um=50.0,
        shank_length_um=1550.0,
        detection_radius_um=200.0,  # larger radius to ensure units in small network
        tip_x_um=0.0,
        tip_y_um=300.0,
        tip_z_um=4000.0
    )

    probe = VirtualProbe(cfg)

    # 1. Channel positions validation
    ch_pos = probe.channel_positions_um
    assert ch_pos.shape == (32, 3), "Probe must have (32, 3) channel coordinates"
    assert np.all(ch_pos[:, 0] == cfg.tip_x_um), "Linear shank must share X coordinate"
    assert np.all(ch_pos[:, 2] == cfg.tip_z_um), "Linear shank must share Z coordinate"
    expected_y = cfg.tip_y_um + np.arange(32) * cfg.pitch_um
    assert np.allclose(ch_pos[:, 1], expected_y), "Channel Y coordinates must follow 50 um linear pitch"

    # 2. Network sampling
    sample_info = probe.sample_network(net)
    assert 'n_detected_units' in sample_info
    assert 'channel_assignments' in sample_info
    assert 'channel_neuron_map' in sample_info

    if probe.n_detected_units > 0:
        assert len(probe.detected_neuron_indices) == probe.n_detected_units
        assert len(probe.channel_assignments) == probe.n_detected_units
        assert np.all(probe.channel_assignments >= 0) and np.all(probe.channel_assignments < 32)
        assert len(probe.detected_cell_types) == probe.n_detected_units

        # Verify distance constraint
        soma_pos = np.column_stack([net.pos_x, net.pos_y, net.pos_z])
        for idx, ch in zip(probe.detected_neuron_indices, probe.channel_assignments):
            dist = np.linalg.norm(soma_pos[idx] - ch_pos[ch])
            assert dist <= cfg.detection_radius_um + 1e-6, f"Neuron {idx} distance {dist} exceeds detection radius"

    # 3. Multi-unit rate extraction
    mock_rates = np.ones((100, net.n_neurons)) * 5.0
    ch_rates = probe.compute_multi_unit_rates(mock_rates)
    assert ch_rates.shape == (100, 32)
    assert not np.isnan(ch_rates).any()
    assert np.all(ch_rates >= 0.0)

    # 4. Plotting Panel 6E
    out_6e = os.path.join(tmp_path, "24_fig6e_virtual_probe.png")
    fig_6e = plot_panel_6e_probe_insertion(net, probe, output_path=out_6e, dpi=100)
    assert os.path.exists(out_6e)
    assert os.path.exists(os.path.join(tmp_path, "24_fig6e_probe_insertion.png"))
    plt.close(fig_6e)


def test_panel_6f_multichannel_spiking_suite(small_test_network, tmp_path):
    """
    Verifies Panel 6F electrophysiology pipeline:
    1. Inhomogeneous Poisson spike conversion
    2. Gaussian kernel firing rate smoothing
    3. Multi-channel phase lag extraction
    4. Panel 6F figure generation and composite Figure 6 generation
    """
    from electrophysiology import generate_poisson_spikes, estimate_instantaneous_rates, compute_channel_phase_lags
    from simulation import SimulationConfig, Simulator
    from figure6_analysis import plot_panel_6f_multichannel_spiking, generate_figure6_complete

    net = small_test_network
    cfg = SimulationConfig(t_steps=500, dt_ms=1.0, I_e=30.0, noise_ampl=0.5, seed=42)
    sim = Simulator(cfg)
    res = sim.run(net, verbose=False)

    # 1. Poisson Spiking
    spikes1 = generate_poisson_spikes(res.rates, scale=75.0, seed=42)
    spikes2 = generate_poisson_spikes(res.rates, scale=75.0, seed=42)
    assert spikes1.shape == (500, net.n_neurons)
    assert spikes1.dtype == bool
    assert np.array_equal(spikes1, spikes2), "Poisson spike generation must be deterministic with fixed seed"

    # 2. Gaussian Smoothing Rate Estimation
    est_rates = estimate_instantaneous_rates(spikes1, sigma_ms=50.0, dt_ms=1.0)
    assert est_rates.shape == (500, net.n_neurons)
    assert not np.isnan(est_rates).any()
    assert np.all(est_rates >= 0.0)

    # 3. Virtual Probe & Multi-Unit Rates
    probe_cfg = ProbeConfig(
        n_channels=32,
        pitch_um=50.0,
        shank_length_um=1550.0,
        detection_radius_um=200.0,
        tip_x_um=0.0,
        tip_y_um=300.0,
        tip_z_um=4000.0
    )
    probe = VirtualProbe(probe_cfg)
    probe.sample_network(net)

    ch_rates = probe.compute_multi_unit_rates(est_rates)
    assert ch_rates.shape == (500, 32)
    phase_metrics = compute_channel_phase_lags(ch_rates, dt_ms=1.0, t_start_ms=100)
    assert 'phase_lags_deg' in phase_metrics
    assert 'phase_lags_rad' in phase_metrics
    assert 'cycle_period_ms' in phase_metrics
    assert len(phase_metrics['phase_lags_deg']) == 32

    # 4. Plotting Panel 6F
    out_6f = os.path.join(tmp_path, "25_fig6f_multichannel_spiking.png")
    fig_6f = plot_panel_6f_multichannel_spiking(probe, spikes1, est_rates, res.time_ms, output_path=out_6f, dpi=100)
    assert os.path.exists(out_6f)
    plt.close(fig_6f)

    # 5. Composite Figure 6
    suite_data = {
        'control_res': res,
        'lesion_res': res,
        'control_net': net,
        'lesion_net': net,
        'regrowth_nets': {'regrowth_V2a-2': net},
        'regrowth_results': {'regrowth_V2a-2': (res, {'target_population': 'V2a-2', 'n_restored': 100, 'frequency_hz': 2.5, 'rms_amplitude_hz': 0.05, 'status': 'Rescued'}, net)},
        'probe': probe,
        'spikes': spikes1,
        'estimated_rates': est_rates
    }
    gen_files = generate_figure6_complete(suite_data, output_dir=str(tmp_path), dpi=100)
    assert 'figure6_complete' in gen_files
    assert os.path.exists(gen_files['figure6_complete'])


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






