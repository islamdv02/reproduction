"""
Unit tests for Figure 3 Locomotion Analysis Module.
Validates synthetic EMG, traveling wave propagation, PCA neural manifold,
and inter-population phase calculations.
"""

import sys
import os
import pytest
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
try:
    from network import Network
    from simulation import SimulationConfig, Simulator
    from locomotion import (
        generate_synthetic_emg,
        compute_traveling_wave,
        compute_pca_dynamics,
        compute_population_phases,
        generate_poisson_spikes_and_rates,
        MUSCLE_FLEX_EXT
    )
except ImportError:
    from src.network import Network
    from src.simulation import SimulationConfig, Simulator
    from src.locomotion import (
        generate_synthetic_emg,
        compute_traveling_wave,
        compute_pca_dynamics,
        compute_population_phases,
        generate_poisson_spikes_and_rates,
        MUSCLE_FLEX_EXT
    )


@pytest.fixture(scope="module")
def baseline_simulation():
    """Builds a small test network and runs 500 ms simulation for fast testing."""
    net = Network(
        segments=['L1', 'L2', 'L3'],
        density=0.8,
        symmetry=True,
        balance=True,
        rescale=True,
        rng_seed=42,
        compute_eigenspectrum=False
    )
    cfg = SimulationConfig(t_steps=500, I_e=30.0, seed=5)
    sim = Simulator(cfg)
    res = sim.run(net, verbose=False)
    return net, res


def test_synthetic_emg_generation(baseline_simulation):
    net, res = baseline_simulation
    emg_res = generate_synthetic_emg(
        rates=res.rates,
        neuron_types=net.types,
        neuron_lat=net.pos_x,
        neuron_z=net.pos_z,
        time_ms=res.time_ms,
        noise_level=0.1,
        window_ms=20,
        rng_seed=42
    )
    assert 'Right' in emg_res and 'Left' in emg_res
    for side in ['Right', 'Left']:
        s_data = emg_res[side]
        assert len(s_data['muscles']) == len(MUSCLE_FLEX_EXT)
        assert s_data['raw_emg'].shape == (500, len(MUSCLE_FLEX_EXT))
        assert s_data['envelope'].shape == (500, len(MUSCLE_FLEX_EXT))
        assert np.all(np.isfinite(s_data['raw_emg']))
        assert np.all(np.isfinite(s_data['envelope']))
        assert np.all(s_data['envelope'] >= 0.0)


def test_traveling_wave_computation(baseline_simulation):
    net, res = baseline_simulation
    wave = compute_traveling_wave(
        rates=res.rates,
        neuron_z=net.pos_z,
        dt_ms=1.0,
        t_start_ms=100,
        n_spatial_bins=10
    )
    assert 'wave_velocity_mm_s' in wave
    assert 'spatial_phases_rad' in wave
    assert len(wave['spatial_phases_rad']) == 10
    assert wave['cycle_period_ms'] > 0.0
    assert wave['loco_frequency_hz'] > 0.0
    assert np.all(np.isfinite(wave['spatial_lags_ms']))


def test_pca_dynamics_computation(baseline_simulation):
    net, res = baseline_simulation
    pca = compute_pca_dynamics(
        rates=res.rates,
        n_components=3,
        t_start_ms=100
    )
    assert pca['pcs'].shape == (400, 3)
    assert len(pca['explained_variance_ratio']) == 3
    assert np.all(pca['explained_variance_ratio'] >= 0.0)
    assert np.isclose(np.sum(pca['explained_variance_ratio']), pca['cumulative_variance'][-1])
    assert pca['cumulative_variance'][-1] > 0.0


def test_population_phase_relationships(baseline_simulation):
    net, res = baseline_simulation
    phase_data = compute_population_phases(
        population_rates=res.population_rates,
        dt_ms=1.0,
        t_start_ms=100,
        reference_pop='V2a-1'
    )
    assert 'phases_rad' in phase_data
    assert 'cycle_period_ms' in phase_data
    assert phase_data['cycle_period_ms'] > 0.0
    for pop_name, phase_rad in phase_data['phases_rad'].items():
        assert 0.0 <= phase_rad <= 2.0 * np.pi + 1e-6


def test_poisson_spikes_and_gaussian_rates(baseline_simulation):
    net, res = baseline_simulation
    spikes, g_rates = generate_poisson_spikes_and_rates(
        rates=res.rates[:100, :10],
        scale_factor=40.0,
        gaussian_std_ms=20.0,
        rng_seed=42
    )
    assert spikes.shape == (100, 10)
    assert g_rates.shape == (100, 10)
    assert np.all(np.isin(spikes, [0.0, 1.0]))
    assert np.all(g_rates >= 0.0)
    assert np.all(np.isfinite(g_rates))
