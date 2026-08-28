"""
Tests for traveling wave propagation, velocity, and bilateral alternation.
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
from traveling_wave import TravelingWaveAnalyzer


def test_traveling_wave_grid_and_metrics():
    net = YakovenkoKomiSpatialNetwork(n_neurons=300, rng_seed=42)
    conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=42)
    dyn = RecurrentRateDynamics(conn, rng_seed=42)
    times, rates, _ = dyn.simulate(duration_ms=1200.0, warmup_ms=300.0)

    wave = TravelingWaveAnalyzer(net, rates, times)
    assert wave.grid.shape == (30, len(times))
    assert wave.velocity_mm_s > 0.0
    assert 0.0 <= wave.bilateral_phase_diff_deg <= 180.0
    assert -1.0 <= wave.alternation_index <= 1.0
