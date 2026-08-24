"""
Unit tests for Neural Dynamics and Simulation engine.
Verifies rate activation bounds, Euler integration, output shapes,
reproducibility with random seeds, stability (no NaNs), and synaptic coupling.
"""

import os
import sys
import pytest
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from network import Network, NetworkParameters
from dynamics import (
    tanh_activation,
    euler_step_voltage,
    euler_step_adaptation,
    compute_spectral_analysis
)
from simulation import SimulationConfig, Simulator, SimulationResult


def test_tanh_activation_limits():
    threshold = 5.0
    gain = 1.0
    f_max = 50.0

    # 1. At threshold (V = 5.0)
    rate_th = tanh_activation(threshold, threshold, gain, f_max)
    assert np.isclose(rate_th, threshold, atol=1e-6), f"Rate at threshold must equal {threshold}"

    # 2. Deep hyperpolarization (V = -1000.0) -> rate -> 0
    rate_hyper = tanh_activation(-1000.0, threshold, gain, f_max)
    assert np.isclose(rate_hyper, 0.0, atol=1e-4), "Rate under strong hyperpolarization must approach 0"

    # 3. Strong depolarization (V = 1000.0) -> rate -> threshold + f_max
    rate_depol = tanh_activation(1000.0, threshold, gain, f_max)
    assert np.isclose(rate_depol, threshold + f_max, atol=1e-4), f"Rate under strong depolarization must approach {threshold + f_max}"

    # 4. Non-negativity across wide voltage range
    v_range = np.linspace(-200.0, 200.0, 500)
    rates = tanh_activation(v_range, threshold, gain, f_max)
    assert np.all(rates >= 0.0), "Firing rates must be strictly non-negative"


def test_euler_step_voltage():
    v_prev = -70.0
    i_tot = 30.0
    tau_v = 50.0
    dt = 1.0

    # Expected: -70 + (-(-70) + 30)/50 * 1 = -70 + (70+30)/50 = -70 + 2 = -68.0
    v_next = euler_step_voltage(v_prev, i_tot, tau_v, dt=dt)
    assert np.isclose(v_next, -68.0), f"Expected -68.0, got {v_next}"


@pytest.fixture(scope="module")
def small_network():
    segments = ['L1', 'L2']
    net = Network(segments=segments, density=0.4, symmetry=True, balance=True, rescale=True, rng_seed=42, compute_eigenspectrum=False)
    return net


def test_simulation_state_dimensions(small_network):
    net = small_network
    t_steps = 200
    cfg = SimulationConfig(t_steps=t_steps, seed=42)
    sim = Simulator(cfg)
    res = sim.run(net, verbose=False)

    assert res.rates.shape == (t_steps, net.n_neurons), f"Rates shape mismatch: {res.rates.shape}"
    assert res.voltage.shape == (t_steps, net.n_neurons), f"Voltage shape mismatch: {res.voltage.shape}"
    assert len(res.time_ms) == t_steps
    assert len(res.final_voltage) == net.n_neurons
    assert len(res.final_rates) == net.n_neurons


def test_simulation_reproducibility(small_network):
    net = small_network
    cfg1 = SimulationConfig(t_steps=100, seed=12345)
    sim1 = Simulator(cfg1)
    res1 = sim1.run(net, verbose=False)

    cfg2 = SimulationConfig(t_steps=100, seed=12345)
    sim2 = Simulator(cfg2)
    res2 = sim2.run(net, verbose=False)

    assert np.array_equal(res1.rates, res2.rates), "Simulations with same seed must be identical"
    assert np.array_equal(res1.voltage, res2.voltage), "Simulations with same seed must be identical"


def test_finite_non_nan_activity(small_network):
    net = small_network
    cfg = SimulationConfig(t_steps=500, I_e=30.0, seed=5)
    sim = Simulator(cfg)
    res = sim.run(net, verbose=False)

    assert not np.any(np.isnan(res.rates)), "Firing rates must not contain NaNs"
    assert not np.any(np.isinf(res.rates)), "Firing rates must not contain Infs"
    assert not np.any(np.isnan(res.voltage)), "Voltages must not contain NaNs"
    assert not np.any(np.isinf(res.voltage)), "Voltages must not contain Infs"


def test_recurrent_weights_connected(small_network):
    net = small_network
    cfg = SimulationConfig(t_steps=100, I_e=30.0, seed=42)
    
    # Run with original connectivity
    sim = Simulator(cfg)
    res_connected = sim.run(net, verbose=False)

    # Temporarily zero out weights to simulate uncoupled network
    orig_w = net.conn_mat.copy()
    net.conn_mat = np.zeros_like(orig_w)
    res_uncoupled = sim.run(net, verbose=False)
    net.conn_mat = orig_w # Restore

    # Firing rates must differ due to synaptic feedback
    diff = np.max(np.abs(res_connected.rates - res_uncoupled.rates))
    assert diff > 1e-3, "Recurrent synaptic connectivity must alter rate dynamics"
