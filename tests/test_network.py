"""
Unit tests for Network and Connectivity construction.
Verifies population sizing, spatial bounding boxes, autapse exclusion,
Dale's principle, E/I balance, and matrix validity.
"""

import os
import sys
import pytest
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
try:
    from data_loader import SpinalDataLoader
    from network import Celltype, NetworkParameters, Network
    from connectivity import (
        compute_pairwise_distances,
        compute_directional_biases,
        compute_connection_probabilities,
        sample_connectivity_matrix,
        balance_connectivity,
        rescale_connectivity
    )
except ImportError:
    from src.data_loader import SpinalDataLoader
    from src.network import Celltype, NetworkParameters, Network
    from src.connectivity import (
        compute_pairwise_distances,
        compute_directional_biases,
        compute_connection_probabilities,
        sample_connectivity_matrix,
        balance_connectivity,
        rescale_connectivity
    )


@pytest.fixture(scope="module")
def default_network():
    segments = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4']
    net = Network(segments=segments, density=0.8, symmetry=True, balance=True, rescale=True, rng_seed=42, compute_eigenspectrum=False)
    return net


def test_expected_neuron_population_size(default_network):
    net = default_network
    assert net.n_neurons > 0, "Network must contain a non-zero number of neurons"
    assert len(net.pos_x) == net.n_neurons
    assert len(net.pos_y) == net.n_neurons
    assert len(net.pos_z) == net.n_neurons
    assert net.conn_mat.shape == (net.n_neurons, net.n_neurons)


def test_valid_cell_type_assignments(default_network):
    net = default_network
    configured_types = set(net.parameters.celltypes.keys())
    sampled_types = set(net.types)
    assert sampled_types.issubset(configured_types), "All sampled neuron types must be in configured populations"
    assert len(sampled_types) > 1, "Network must contain multiple cell types"


def test_valid_spatial_coordinates(default_network):
    net = default_network
    assert net.pos_x.min() >= -2000.0 and net.pos_x.max() <= 2000.0, "X coordinates out of physical bounds"
    assert net.pos_y.min() >= -100.0 and net.pos_y.max() <= 2000.0, "Y coordinates out of physical bounds"
    # Rostrocaudal Z (T13-S4 total length is ~13,900 um)
    assert net.pos_z.min() >= 0.0 and net.pos_z.max() <= 15000.0, "Z coordinates out of physical bounds"


def test_no_self_connections(default_network):
    net = default_network
    diag_elements = np.diag(net.conn_mat)
    assert np.all(diag_elements == 0.0), "No neuron should have a self-connection (autapse)"


def test_dales_principle(default_network):
    net = default_network
    w = net.conn_mat
    is_excit = (net.transmitters > 0)
    is_inhib = (net.transmitters < 0)

    # Excitatory presynaptic columns must have non-negative weights
    assert np.all(w[:, is_excit] >= -1e-10), "Excitatory columns have negative weights (Dale violation)"
    # Inhibitory presynaptic columns must have non-positive weights
    assert np.all(w[:, is_inhib] <= 1e-10), "Inhibitory columns have positive weights (Dale violation)"


def test_expected_ei_organization(default_network):
    net = default_network
    n_excit = np.sum(net.transmitters > 0)
    n_inhib = np.sum(net.transmitters < 0)
    assert n_excit > 0, "Network must contain excitatory neurons"
    assert n_inhib > 0, "Network must contain inhibitory neurons"
    
    n_pos_syn = np.count_nonzero(net.conn_mat > 0)
    n_neg_syn = np.count_nonzero(net.conn_mat < 0)
    assert n_pos_syn > 0, "Network must contain functional excitatory synapses"
    assert n_neg_syn > 0, "Network must contain functional inhibitory synapses"


def test_connectivity_matrix_dimensions(default_network):
    net = default_network
    assert net.conn_mat.ndim == 2
    assert net.conn_mat.shape[0] == net.conn_mat.shape[1] == net.n_neurons


def test_synaptic_weight_validity(default_network):
    net = default_network
    assert not np.any(np.isnan(net.conn_mat)), "Connectivity matrix must not contain NaNs"
    assert not np.any(np.isinf(net.conn_mat)), "Connectivity matrix must not contain Infs"


def test_balance_connectivity():
    rng = np.random.default_rng(42)
    w_test = np.zeros((4, 4))
    w_test[0, 1] = 5.0
    w_test[0, 2] = -1.0
    
    w_bal = balance_connectivity(w_test)
    assert w_bal[0, 0] == 0.0
    assert np.isclose(np.sum(w_bal[0, :]), 0.0, atol=1e-5), "Balanced row must have zero net sum"
