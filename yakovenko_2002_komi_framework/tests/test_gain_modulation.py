"""
Tests for decoupled gain control (excitatory amplitude vs inhibitory frequency).
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from spatial_mapping import YakovenkoKomiSpatialNetwork
from gain_modulation import DecoupledGainController


def test_gain_sweeps():
    net = YakovenkoKomiSpatialNetwork(n_neurons=250, rng_seed=42)
    ctrl = DecoupledGainController(net)

    gains = [0.9, 1.0, 1.1]
    res_exc = ctrl.sweep_excitatory_gain(gains)
    res_inh = ctrl.sweep_inhibitory_gain(gains)

    assert len(res_exc['gains']) == 3
    assert len(res_exc['orbit_radii']) == 3
    assert len(res_inh['frequencies_hz']) == 3
