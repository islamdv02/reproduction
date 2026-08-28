"""
Tests for motor output synthesis and comparison against empirical EMG.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from spatial_mapping import YakovenkoKomiSpatialNetwork, MUSCLE_NAMES
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics
from traveling_wave import TravelingWaveAnalyzer
from motor_mapping import MotorOutputMapper


def test_motor_output_synthesis():
    net = YakovenkoKomiSpatialNetwork(n_neurons=300, rng_seed=42)
    conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=42)
    dyn = RecurrentRateDynamics(conn, rng_seed=42)
    times, rates, _ = dyn.simulate(duration_ms=1000.0, warmup_ms=200.0)

    wave = TravelingWaveAnalyzer(net, rates, times)
    motor = MotorOutputMapper(wave)

    assert motor.simulated_emg.shape == (len(MUSCLE_NAMES), len(times))
    assert len(motor.correlations) == 27
    assert len(motor.nrmse) == 27
    assert -1.0 <= motor.mean_correlation <= 1.0
    assert motor.mean_nrmse >= 0.0
