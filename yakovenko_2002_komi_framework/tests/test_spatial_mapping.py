"""
Tests for 3D spatial embedding of Yakovenko cat anatomy into continuous coordinates.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from spatial_mapping import YakovenkoKomiSpatialNetwork, MUSCLE_NAMES


def test_spatial_network_dimensions():
    net = YakovenkoKomiSpatialNetwork(n_neurons=500, rng_seed=42)
    assert net.n_neurons == 500
    assert net.x.shape == (500,)
    assert net.y.shape == (500,)
    assert net.z.shape == (500,)
    assert np.all(net.z >= 0.0)
    assert np.all(net.z <= 28.8)


def test_hemicord_and_populations():
    net = YakovenkoKomiSpatialNetwork(n_neurons=500, rng_seed=42)
    assert len(net.population) == 500
    assert np.sum(net.hemicord == 'left') > 0
    assert np.sum(net.hemicord == 'right') > 0
    assert np.sum(net.is_commissural) > 0
    assert np.sum(net.is_excitatory) > 0
    assert np.sum(~net.is_excitatory) > 0


def test_slice_index_conversion():
    net = YakovenkoKomiSpatialNetwork(n_neurons=100, rng_seed=42)
    assert net.get_slice_index(0.5) == 0
    assert net.get_slice_index(14.4) == 15
    assert net.get_slice_index(28.5) == 29
