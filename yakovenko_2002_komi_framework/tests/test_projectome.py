"""
Tests for 1D net projectome profile and Mexican-hat indices.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from projectome_analysis import ProjectomeAnalyzer


def test_projectome_1d_profile_and_mexican_hat():
    net = YakovenkoKomiSpatialNetwork(n_neurons=400, rng_seed=42)
    conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=42)
    proj = ProjectomeAnalyzer(conn, n_bins=41)

    assert len(proj.bin_centers) == 41
    assert len(proj.net_profile) == 41
    assert -1.0 <= proj.asymmetry_index <= 1.0
    assert 0.0 <= proj.mexican_hat_index <= 1.0
