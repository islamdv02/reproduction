"""
Tests for PCA decomposition, circular phase sorting, and limit cycle metrics.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics
from phase_analysis import PhaseUnfolder


def test_pca_and_phase_unfolding():
    net = YakovenkoKomiSpatialNetwork(n_neurons=300, rng_seed=42)
    conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=42)
    dyn = RecurrentRateDynamics(conn, rng_seed=42)
    times, rates, _ = dyn.simulate(duration_ms=1200.0, warmup_ms=300.0)

    pu = PhaseUnfolder(rates, times)
    assert 0.0 <= pu.planar_variance <= 1.0
    assert pu.orbit_radius > 0.0
    assert len(pu.phase_angles) == 300
    assert np.all(pu.phase_angles >= 0.0)
    assert np.all(pu.phase_angles < 2.0 * np.pi)
    assert len(pu.phase_sorted_indices) == 300
