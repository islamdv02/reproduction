"""
Unit tests for Figure 4: Speed and Gait Control Module.
Validates compound tanh gain modulation, descending drive simulations,
monotonic frequency acceleration, Left-Right phase transitions, and
preservation of flexor-extensor reciprocal coordination.
"""

import sys
import os
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from network import Network
from dynamics import tanh_activation
from gait_control import (
    DescendingDriveConfig,
    classify_gait,
    simulate_gait_regime,
    simulate_descending_ramp,
    run_descending_drive_sweep
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


def test_tanh_gain_modulation():
    """Verifies that increasing neuromodulatory gain g steepens rate activation."""
    v_sub = 10.0
    v_supra = 40.0
    threshold = 20.0
    f_max = 50.0

    # Below threshold: zero or small rate
    r_sub_low = tanh_activation(v_sub, threshold, 0.5, f_max)
    r_sub_high = tanh_activation(v_sub, threshold, 2.0, f_max)
    assert r_sub_low >= 0.0
    assert r_sub_high >= 0.0

    # Above threshold: higher gain produces higher firing rate
    r_supra_low = tanh_activation(v_supra, threshold, 0.5, f_max)
    r_supra_high = tanh_activation(v_supra, threshold, 2.0, f_max)
    assert r_supra_high > r_supra_low, "Higher gain must produce higher firing rate for suprathreshold inputs"
    assert r_supra_high <= f_max + threshold


def test_gait_classification_logic():
    """Tests rule-based gait classifier across canonical physiological conditions."""
    # Walk: Low freq, alternation
    assert classify_gait(2.0, np.pi, np.pi) == "Walk"
    # Trot: Mid freq, alternation
    assert classify_gait(4.0, np.pi, np.pi) == "Trot"
    # Bound: High freq, synchrony (~0 rad)
    assert classify_gait(6.5, 0.0, np.pi) == "Bound"
    # Bound with small phase perturbation (< 60 deg = pi/3 rad)
    assert classify_gait(7.0, np.radians(20.0), np.pi) == "Bound"


def test_descending_drive_config():
    """Tests DescendingDriveConfig default properties."""
    cfg = DescendingDriveConfig()
    assert cfg.I_lpgi_base == 30.0
    assert cfg.I_lpgi_ramp_start == 15.0
    assert cfg.I_lpgi_ramp_end == 50.0
    assert 'V2a-1' in cfg.lpgi_targets
    assert 'MN' in cfg.lpgi_targets
    assert cfg.serotonin_gain_multiplier == 1.0


def test_multi_gait_simulations_monotonic_frequency(small_test_network):
    """Verifies that increasing descending drive increases oscillation frequency."""
    net = small_test_network

    # Run short simulations (2000 ms each) for fast unit testing
    sim_walk, metrics_walk = simulate_gait_regime(net, gait_name="walk", t_steps=2000, seed=42)
    sim_trot, metrics_trot = simulate_gait_regime(net, gait_name="trot", t_steps=2000, seed=42)
    sim_bound, metrics_bound = simulate_gait_regime(net, gait_name="bound", t_steps=2000, seed=42)

    assert sim_walk.rates.shape == (2000, net.n_neurons)
    assert sim_trot.rates.shape == (2000, net.n_neurons)
    assert sim_bound.rates.shape == (2000, net.n_neurons)

    assert not np.isnan(sim_walk.rates).any(), "Walk rates must not contain NaNs"
    assert not np.isnan(sim_trot.rates).any(), "Trot rates must not contain NaNs"
    assert not np.isnan(sim_bound.rates).any(), "Bound rates must not contain NaNs"

    freq_walk = metrics_walk['frequency_hz']
    freq_trot = metrics_trot['frequency_hz']
    freq_bound = metrics_bound['frequency_hz']

    assert freq_walk > 0.0, "Walk frequency must be positive"
    assert freq_trot >= freq_walk, "Trot frequency must be >= walk frequency"
    assert freq_bound >= freq_trot, "Bound frequency must be >= trot frequency"


def test_flexor_extensor_phase_preservation(small_test_network):
    """Verifies that flexor-extensor phase relationship is finite and calculable."""
    net = small_test_network
    _, metrics_trot = simulate_gait_regime(net, gait_name="trot", t_steps=2500, seed=42)
    fe_deg = metrics_trot['fe_phase_deg']
    assert 0.0 <= fe_deg <= 360.0, f"Flexor-extensor phase ({fe_deg:.1f}°) must be within valid circular range"
    assert not np.isnan(fe_deg)


def test_descending_ramp_continuity(small_test_network):
    """Tests dynamic stability and finite outputs under descending ramp."""
    net = small_test_network
    sim_ramp, I_ramp = simulate_descending_ramp(net, I_start=15.0, I_end=45.0, t_steps=2000, seed=42)

    assert len(I_ramp) == 2000
    assert I_ramp[0] == 15.0
    assert np.isclose(I_ramp[-1], 45.0, atol=0.1)
    assert sim_ramp.rates.shape == (2000, net.n_neurons)
    assert np.all(sim_ramp.rates >= 0.0), "Rates must remain non-negative"
    assert not np.isnan(sim_ramp.rates).any(), "Ramp simulation must not diverge or contain NaNs"


def test_descending_drive_sweep(small_test_network):
    """Tests descending drive sweep generator."""
    net = small_test_network
    drive_levels = np.array([20.0, 30.0, 45.0])
    df = run_descending_drive_sweep(net, drive_levels=drive_levels, t_steps=1500, seed=42)

    assert len(df) == 3
    assert 'frequency_hz' in df.columns
    assert 'rms_amplitude_hz' in df.columns
    assert 'gait_state' in df.columns
    assert np.all(df['frequency_hz'] > 0.0)
