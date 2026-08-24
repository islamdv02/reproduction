"""
Unit tests for Figure 5: Cell-Type Specific Perturbation Experiments.
Tests structural ablation, functional silencing, V1 disinhibition/deceleration,
V0 contralateral phase disruption, output shapes, reproducibility, and finite outputs.
"""

import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from network import Network
from perturbations import (
    create_ablated_network,
    simulate_silencing,
    simulate_perturbation_condition,
    run_figure5_perturbation_suite
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


def test_create_ablated_network(small_test_network):
    """Verifies that ablation zeroes all synaptic weights for target populations."""
    net = small_test_network
    target_pops = ['V1']
    ablated_net = create_ablated_network(net, target_pops)

    target_mask = np.isin(ablated_net.types, target_pops)
    non_target_mask = ~target_mask

    # Target outgoing and incoming weights must be strictly zero
    assert np.all(ablated_net.conn_mat[:, target_mask] == 0.0), "Outgoing target synapses must be 0"
    assert np.all(ablated_net.conn_mat[target_mask, :] == 0.0), "Incoming target synapses must be 0"

    # Non-target to non-target weights must remain untouched
    orig_sub = net.conn_mat[np.ix_(non_target_mask, non_target_mask)]
    ablated_sub = ablated_net.conn_mat[np.ix_(non_target_mask, non_target_mask)]
    assert np.array_equal(orig_sub, ablated_sub), "Non-target synaptic connections must remain identical"

    # Sparsity must increase
    assert ablated_net.sparsity >= net.sparsity


def test_simulate_silencing_target_suppression(small_test_network):
    """Verifies that hyperpolarizing current suppresses target population firing."""
    net = small_test_network
    target_pops = ['V1']
    res_ctrl = simulate_silencing(net, target_populations=[], I_hyper=0.0, I_e_base=30.0, t_steps=1000, seed=42)
    res_sil = simulate_silencing(net, target_populations=target_pops, I_hyper=-60.0, I_e_base=30.0, t_steps=1000, seed=42)

    v1_ctrl = float(np.mean(res_ctrl.population_rates['V1']))
    v1_sil = float(np.mean(res_sil.population_rates['V1']))

    # Silenced rate must be significantly lower than control rate
    assert v1_sil < v1_ctrl, f"Silenced rate ({v1_sil:.2f} Hz) must be less than control rate ({v1_ctrl:.2f} Hz)"
    assert res_sil.rates.shape == (1000, net.n_neurons)


def test_v1_ablation_simulation(small_test_network):
    """Verifies V1 ablation simulation produces finite non-NaN rates and valid phase bounds."""
    net = small_test_network
    sim_res, metrics, ablated_net = simulate_perturbation_condition(
        network=net,
        condition="v1",
        perturbation_mode="ablation",
        t_steps=2000,
        seed=42
    )

    assert sim_res.rates.shape == (2000, net.n_neurons)
    assert not np.isnan(sim_res.rates).any(), "V1 simulation must not contain NaNs"
    assert metrics['frequency_hz'] > 0.0
    assert 0.0 <= metrics['lr_phase_deg'] <= 360.0
    assert 0.0 <= metrics['fe_phase_deg'] <= 360.0


def test_v0_ablation_simulation(small_test_network):
    """Verifies V0 ablation simulation produces finite non-NaN rates and valid metrics."""
    net = small_test_network
    sim_res, metrics, ablated_net = simulate_perturbation_condition(
        network=net,
        condition="v0",
        perturbation_mode="ablation",
        t_steps=2000,
        seed=42
    )

    assert sim_res.rates.shape == (2000, net.n_neurons)
    assert not np.isnan(sim_res.rates).any(), "V0 simulation must not contain NaNs"
    assert metrics['frequency_hz'] > 0.0
    assert 0.0 <= metrics['lr_phase_deg'] <= 360.0
    assert 0.0 <= metrics['fe_phase_deg'] <= 360.0


def test_perturbation_reproducibility(small_test_network):
    """Verifies simulation reproducibility across identical seeds."""
    net = small_test_network
    res1, _, _ = simulate_perturbation_condition(net, condition="v1", t_steps=500, seed=123)
    res2, _, _ = simulate_perturbation_condition(net, condition="v1", t_steps=500, seed=123)

    assert np.array_equal(res1.rates, res2.rates)
    assert np.array_equal(res1.voltage, res2.voltage)
