"""
Tests for 3D connectome construction, Dale's law, and row-wise zero-sum E/I balancing.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome


def test_connectome_shape_and_density():
    net = YakovenkoKomiSpatialNetwork(n_neurons=400, rng_seed=42)
    conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=42)
    assert conn.W.shape == (400, 400)
    assert 0.005 <= conn.density <= 0.30


def test_dales_law_conformity():
    net = YakovenkoKomiSpatialNetwork(n_neurons=300, rng_seed=42)
    conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=42)
    for j in range(net.n_neurons):
        if net.is_excitatory[j]:
            assert np.all(conn.W[:, j] >= 0.0), f"Excitatory neuron {j} has negative weights"
        else:
            assert np.all(conn.W[:, j] <= 0.0), f"Inhibitory neuron {j} has positive weights"


def test_row_wise_zero_sum_balance():
    net = YakovenkoKomiSpatialNetwork(n_neurons=400, rng_seed=42)
    conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=42)
    assert abs(conn.mean_row_sum) < 0.1
    # Check that majority of rows with both E and I inputs are near zero
    row_sums = np.sum(conn.W, axis=1)
    assert np.median(np.abs(row_sums)) < 0.05
