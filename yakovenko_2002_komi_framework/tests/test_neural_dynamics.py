"""
Tests for Forward Euler leaky rate integration and compound tanh activation function.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics, compound_tanh


def test_compound_tanh_activation():
    I_neg = np.array([-10.0, -5.0, 0.0])
    assert np.all(compound_tanh(I_neg) == 0.0)

    I_pos = np.array([10.0, 50.0, 100.0, 1000.0])
    f_val = compound_tanh(I_pos, f_max=100.0)
    assert np.all(f_val > 0.0)
    assert np.all(f_val <= 100.0)


def test_rate_dynamics_simulation():
    net = YakovenkoKomiSpatialNetwork(n_neurons=300, rng_seed=42)
    conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=42)
    dyn = RecurrentRateDynamics(conn, rng_seed=42)

    times, rates, currents = dyn.simulate(duration_ms=1000.0, warmup_ms=200.0)
    assert len(times) == 800
    assert rates.shape == (300, 800)
    assert np.all(rates >= 0.0)
    assert not np.any(np.isnan(rates))
    assert not np.any(np.isinf(rates))
